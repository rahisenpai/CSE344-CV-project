# global libraries
from ultralytics import YOLO
import cv2
import numpy as np
from .sort.sort import *
import easyocr

reader = easyocr.Reader(['en']) # Initialize the OCR reader
vehicle_detector_model = YOLO('pipeline/helmet-violation-detector-YOLOv8m.pt')
license_plate_detector_model = YOLO('pipeline/license_plate_detector-YOLOv8n.pt')

vehicle_ids = [1] #without_helmet
detection_threshold = 0.1

def detect_vehicles(frame):
    vehicle_detections = []
    detections = vehicle_detector_model(frame)[0]

    for detection in detections.boxes.data.tolist():
        x1, y1, x2, y2, conf_score, class_id = detection
        # taking into consideration the class ids of only vehicles
        if (int(class_id) in vehicle_ids):
            # if conf_score > detection_threshold:
            vehicle_detections.append([x1, y1, x2, y2, conf_score])

    return np.asarray(vehicle_detections)


def read_license_plate(license_plate):

    detections = reader.readtext(license_plate)

    for detection in detections:
        _, text, score = detection

        text = text.upper().translate(str.maketrans('', '', ' ._-'))
        # if license_complies_format(text):
        #     return text, score
        return text, score

    return None, None


def get_vehicle(license_plate, vehicle_track_ids):

    x1, y1, x2, y2, __, _ = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        x1_vehicle, y1_vehicle, x2_vehicle, y2_vehicle, _ = vehicle_track_ids[j]

        if x1 > x1_vehicle and y1 > y1_vehicle and x2 < x2_vehicle and y2 < y2_vehicle:
            vehicle_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[vehicle_indx]

    return -1, -1, -1, -1, -1


def process_license_plate(frame, license_plate):
    x1, y1, x2, y2, conf_score, _ = license_plate

    cropped_license_plate = frame[int(y1): int(y2), int(x1): int(x2), :] # crop
    gray_cropped_license_plate = cv2.cvtColor(cropped_license_plate, cv2.COLOR_BGR2GRAY) #grayscale
    blurred_plate = cv2.GaussianBlur(gray_cropped_license_plate, (5, 5), 0) #removing the gaussian noise using kernels 
    _, license_plate_crop_thresh = cv2.threshold(blurred_plate, 64, 255, cv2.THRESH_BINARY_INV)

    license_plate_text, license_plate_score = read_license_plate(license_plate_crop_thresh)
    return license_plate_text, license_plate_score, conf_score, x1, y1, x2, y2


def write_csv(results, output_path):
    with open(output_path, 'w') as f:
        f.write('frame_no,vehicle_id,vehicle_bbox,license_plate_bbox,license_plate_bbox_score,license_number,license_number_score\n')

        for frame_nmr, vehicles in results.items():
            for vehicle_id, data in vehicles.items():
                vehicle = data.get('vehicle', {}).get('bbox')
                lp_data = data.get('license_plate', {})

                if vehicle and 'text' in lp_data:
                    f.write(f"{frame_nmr},{vehicle_id},[{vehicle[0]} {vehicle[1]} {vehicle[2]} {vehicle[3]}],"
                            f"[{lp_data['bbox'][0]} {lp_data['bbox'][1]} {lp_data['bbox'][2]} {lp_data['bbox'][3]}],"
                            f"{lp_data['bbox_score']},{lp_data['text']},{lp_data['text_score']}\n")


def process_video(video_path: str, output_csv_path='results.csv'):

    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    print(f"Frames per second: {fps}")
    vehicle_tracker = Sort() #object tracker used to track the vehicles in motion
    results = {}

    ret = True   # ret = True implies that more frames in the video are left.
    frame_no = -1


    while (ret):
        frame_no += 1
        print(frame_no)
        # if frame_no < 60:
        #     continue
        # if frame_no > 135:
            # break
        results[frame_no] = {}
        ret, frame = video.read()

        if ret:
            vehicle_detections = detect_vehicles(frame)

            vehicle_track_ids = vehicle_tracker.update(vehicle_detections) # maps each vehicle to some ids for tracking purposes , also gives the bbox for each vehicle

            license_plate_detections = license_plate_detector_model(frame)[0]
            for license_plate in license_plate_detections.boxes.data.tolist():
                # print("helo")
                x1_vehicle, y1_vehicle, x2_vehicle, y2_vehicle, vehicle_id = get_vehicle(license_plate, vehicle_track_ids)

                if (vehicle_id != -1):  # if vehicle-license_plate mapping found
                    license_plate_text, license_plate_score, conf_score_license, x1_license, y1_license, x2_license, y2_license = process_license_plate(frame, license_plate)

                    if (license_plate_text is not None):
                        results[frame_no][vehicle_id] = {'vehicle': {'bbox': [x1_vehicle, y1_vehicle, x2_vehicle, y2_vehicle]},
                                                        'license_plate': {'bbox': [x1_license, y1_license, x2_license, y2_license],
                                                                        'text': license_plate_text,
                                                                        'bbox_score': conf_score_license,
                                                                        'text_score': license_plate_score}}

    write_csv(results, output_csv_path)
    return output_csv_path

# process_video(video, vehicle_tracker)