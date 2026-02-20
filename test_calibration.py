from services.calibration import start_calibration, save_coordinates

coords = start_calibration()

if coords:
    save_coordinates()