import csv
import numpy as np
from scipy.interpolate import interp1d


def interpolate_bounding_boxes(data):
    # Extract necessary data columns from input data
    frame_numbers = np.array([int(row['frame_no']) for row in data])
    vehicle_ids = np.array([int(float(row['vehicle_id'])) for row in data])
    vehicle_bboxes = np.array([list(map(float, row['vehicle_bbox'][1:-1].split())) for row in data])
    license_plate_bboxes = np.array([list(map(float, row['license_plate_bbox'][1:-1].split())) for row in data])

    interpolated_data = []
    unique_vehicle_ids = np.unique(vehicle_ids)
    
    for vehicle_id in unique_vehicle_ids:
        frame_numbers_ = [p['frame_no'] for p in data if int(float(p['vehicle_id'])) == int(float(vehicle_id))]

        # Filter data for a specific vehicle ID
        vehicle_mask = vehicle_ids == vehicle_id
        vehicle_frame_numbers = frame_numbers[vehicle_mask]
        vehicle_bboxes_interpolated = []
        license_plate_bboxes_interpolated = []

        first_frame_number = vehicle_frame_numbers[0]
        last_frame_number = vehicle_frame_numbers[-1]

        for i in range(len(vehicle_bboxes[vehicle_mask])):
            frame_number = vehicle_frame_numbers[i]
            vehicle_bbox = vehicle_bboxes[vehicle_mask][i]
            license_plate_bbox = license_plate_bboxes[vehicle_mask][i]

            if i > 0:
                prev_frame_number = vehicle_frame_numbers[i - 1]
                prev_vehicle_bbox = vehicle_bboxes_interpolated[-1]
                prev_license_plate_bbox = license_plate_bboxes_interpolated[-1]

                if frame_number - prev_frame_number > 1:
                    # Interpolate missing frames' bounding boxes
                    frames_gap = frame_number - prev_frame_number
                    x = np.array([prev_frame_number, frame_number])
                    x_new = np.linspace(prev_frame_number, frame_number, num=frames_gap, endpoint=False)
                    interp_func = interp1d(x, np.vstack((prev_vehicle_bbox, vehicle_bbox)), axis=0, kind='linear')
                    interpolated_vehicle_bboxes = interp_func(x_new)
                    interp_func = interp1d(x, np.vstack((prev_license_plate_bbox, license_plate_bbox)), axis=0, kind='linear')
                    interpolated_license_plate_bboxes = interp_func(x_new)

                    vehicle_bboxes_interpolated.extend(interpolated_vehicle_bboxes[1:])
                    license_plate_bboxes_interpolated.extend(interpolated_license_plate_bboxes[1:])

            vehicle_bboxes_interpolated.append(vehicle_bbox)
            license_plate_bboxes_interpolated.append(license_plate_bbox)

        for i in range(len(vehicle_bboxes_interpolated)):
            frame_number = first_frame_number + i
            row = {}
            row['frame_no'] = str(frame_number)
            row['vehicle_id'] = str(vehicle_id)
            row['vehicle_bbox'] = ' '.join(map(str, vehicle_bboxes_interpolated[i]))
            row['license_plate_bbox'] = ' '.join(map(str, license_plate_bboxes_interpolated[i]))

            if str(frame_number) not in frame_numbers_:
                # Imputed row, set the following fields to '0'
                row['license_plate_bbox_score'] = '0'
                row['license_number'] = '0'
                row['license_number_score'] = '0'
            else:
                # Original row, retrieve values from the input data if available
                original_row = [p for p in data if int(p['frame_no']) == frame_number and int(float(p['vehicle_id'])) == int(float(vehicle_id))][0]
                row['license_plate_bbox_score'] = original_row['license_plate_bbox_score'] if 'license_plate_bbox_score' in original_row else '0'
                row['license_number'] = original_row['license_number'] if 'license_number' in original_row else '0'
                row['license_number_score'] = original_row['license_number_score'] if 'license_number_score' in original_row else '0'

            interpolated_data.append(row)

    return interpolated_data


# Load the CSV file
with open('results.csv', 'r') as file:
    reader = csv.DictReader(file)
    data = list(reader)

# Interpolate missing data
interpolated_data = interpolate_bounding_boxes(data)

# Write updated data to a new CSV file
header = ['frame_no', 'vehicle_id', 'vehicle_bbox', 'license_plate_bbox', 'license_plate_bbox_score', 'license_number', 'license_number_score']
with open('results_interpolated.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()
    writer.writerows(interpolated_data)

print("✅ Interpolation completed! Data saved in 'results_interpolated.csv'.")
