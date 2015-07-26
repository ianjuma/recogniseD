import logging

# cv2 and helper package
from helper.common import cv2, draw_str, os
from helper.video import create_capture

# add face_rec to system path
import sys
sys.path.append("../..")

# lib face_rec imports
from facerec.validation import KFoldCrossValidation
from facerec.serialization import save_model, load_model

# for face detection (you can also use OpenCV2 directly)
from facedet.detector import CascadedDetector
from common.helper import (read_images, ExtendedPredictableModel, get_model)


class App(object):
    def __init__(self, _model, camera_id, cascade_filename):
        self.model = _model
        self.detector = CascadedDetector(
            cascade_fn=cascade_filename, minNeighbors=5, scaleFactor=1.1)
        self.cam = create_capture(camera_id)

    def run(self):
        last_face_recognised = 0
        while True:
            ret, frame = self.cam.read()
            # Resize the frame to half the original size for speeding up the detection process:
            img = cv2.resize(frame, (frame.shape[1] / 2, frame.shape[
                0] / 2), interpolation=cv2.INTER_CUBIC)
            image_out = img.copy()
            for i, r in enumerate(self.detector.detect(img)):
                x0, y0, x1, y1 = r
                # (1) Get face, (2) Convert to grayscale & (3) resize to image_size:
                face = img[y0:y1, x0:x1]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                face = cv2.resize(face, self.model.image_size,
                                  interpolation=cv2.INTER_CUBIC)
                # Get a prediction from the model:
                prediction = self.model.predict(face)[0]
                # class_list = set([1, 2, 3, 4]) - from the folders db-level
                attendees = set([])

                if last_face_recognised != self.model.subject_names[prediction]:
                    attendees.add(self.model.subject_names[prediction])
                    print 'adding'
                    last_face_recognised = self.model.subject_names[prediction]
                    print 'Attending -> %s', [attendees]

                # grab prediction and store in redis - compare lists
                # grab last face variable - only store in imgae var is diff -
                # then add to list - grab date missed - count too
                # Draw the face area in image:
                cv2.rectangle(image_out, (x0, y0), (x1, y1), (0, 255, 0), 2)
                # Draw the predicted name (folder name...):
                draw_str(image_out, (
                    x0 - 20, y0 - 20), self.model.subject_names[prediction])

            cv2.imshow('recognised', image_out)
            # Show image & exit on escape:
            ch = cv2.waitKey(33)
            # just log ch to get key id pressed
            if ch == 1048603:
                break


if __name__ == '__main__':
    from optparse import OptionParser
    # model.pkl is a pickled (hopefully trained) PredictableModel, which is
    # used to make predictions. You can learn a model yourself by passing the
    # parameter -d (or --dataset) to learn the model from a given data-set.
    usage = "usage: %prog [options] model_filename"
    # Add options for training, resizing, validation and setting the camera id:
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-r", "--resize", action="store", type="string", dest="size", default="100x100",
        help="Resizes the given dataset to a given size in format [width]x[height] (default: 100x100).")
    parser.add_option(
        "-v", "--validate", action="store", dest="numfolds", type="int", default=None,
        help="Performs a k-fold cross validation on the dataset, if given (default: None).")
    parser.add_option(
        "-t", "--train", action="store", dest="dataset", type="string", default=None,
        help="Trains the model on the given dataset.")
    parser.add_option(
        "-i", "--id", action="store", dest="camera_id", type="int", default=0,
        help="Sets the Camera Id to be used (default: 0).")
    parser.add_option(
        "-c", "--cascade", action="store", dest="cascade_filename",
        default="classifiers/haarcascade_frontalface_alt2.xml",
        help="Sets path to the Haar Cascade used for the face detection (default: haarcascade_frontalface_alt2.xml).")
    # Show the options to the user:
    parser.print_help()
    print "Press [ESC] to exit the program!"
    print "Script output:"
    # Parse arguments:
    (options, args) = parser.parse_args()
    # Check if a model name was passed:
    if len(args) == 0:
        print "[Error] No prediction model was given."
        sys.exit()
    # This model will be used (or created if the training parameter (-t, --train) exists:
    model_filename = args[0]
    # Check if the given model exists, if no dataset was passed:
    if (options.dataset is None) and (not os.path.exists(model_filename)):
        print "[Error] No prediction model found at '%s'." % model_filename
        sys.exit()
    # Check if the given (or default) cascade file exists:
    if not os.path.exists(options.cascade_filename):
        print "[Error] No Cascade File found at '%s'." % options.cascade_filename
        sys.exit()
    # We are resizing the images to a fixed size, as this is neccessary for some of
    # the algorithms, some algorithms like LBPH don't have this requirement. To
    # prevent problems from popping up, we resize them with a default value if none
    # was given:
    try:
        image_size = (
            int(options.size.split("x")[0]), int(options.size.split("x")[1]))
    except Exception:
        print "[Error] Unable to parse the given image size '%s'. Pass in the format [width]x[height]!" % options.size
        sys.exit()
    # We have got a data set to learn a new model from:
    if options.dataset:
        # Check if the given data set exists:
        if not os.path.exists(options.dataset):
            print "[Error] No data set found at '%s'." % options.dataset
            sys.exit()
        # Reads the images, labels and folder_names from a given data set. Images
        # are re-sized to given size on the fly:
        print "Loading data set..."
        [images, labels, subject_names] = read_images(
            options.dataset, image_size)
        # Zip us a {label, name} dict from the given data:
        list_of_labels = list(xrange(max(labels) + 1))
        subject_dictionary = dict(zip(list_of_labels, subject_names))
        # Get the model we want to compute:
        model = get_model(
            image_size=image_size, subject_names=subject_dictionary)
        # Sometimes you want to know how good the model may perform on the data
        # given, the script allows you to perform a k-fold Cross Validation before
        # the Detection & Recognition part starts:
        if options.numfolds:
            print "Validating model with %s folds..." % options.numfolds
            # We want to have some log output, so set up a new logging handler
            # and point it to stdout:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            # Add a handler to facerec modules, so we see what's going on inside:
            logger = logging.getLogger("facerec")
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            # Perform the validation & print results:
            crossval = KFoldCrossValidation(model, k=options.numfolds)
            crossval.validate(images, labels)
            crossval.print_results()
        # Compute the model:
        print "Computing the model..."
        model.compute(images, labels)
        # And save the model, which uses Pythons pickle module:
        print "Saving the model..."
        save_model(model_filename, model)
    else:
        print "Loading the model..."
        model = load_model(model_filename)
    # We operate on an ExtendedPredictableModel. Quit the application if this
    # isn't what we expect it to be:
    if not isinstance(model, ExtendedPredictableModel):
        print "[Error] The given model is not of type '%s'." % "ExtendedPredictableModel"
        sys.exit()
    # Now it's time to finally start the Application! It simply get's the model
    # and the image size the incoming webcam or video images are resized to:
    print "Starting application..."
    App(_model=model,
        camera_id=options.camera_id,
        cascade_filename=options.cascade_filename).run()
