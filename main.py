from utils import (read_video, save_video)
from trackers import PlayerTracker, BallTracker
from court_line_detector import CourtLineDetector
from mini_court import MiniCourt
import cv2
def main():
    input_video_path = "input_videos/input_video.mp4"
    video_frames = read_video(input_video_path)


    player_tracker = PlayerTracker(model_path='yolov8x')
    ball_tracker = BallTracker(model_path="models\yolov5_last.pt")
    player_detections = player_tracker.detect_frames(video_frames, 
                                                     read_from_stub=True,
                                                     stub_path="tracker_stubs/player_detections.pkl")
    
    ball_detections = ball_tracker.detect_frames(video_frames, 
                                                     read_from_stub=True,
                                                     stub_path="tracker_stubs/ball_detections.pkl")
    
    ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)

    court_model_path = "models\keypoints_model.pth"
    court_line_detector = CourtLineDetector(court_model_path)
    court_keypoints = court_line_detector.predict(video_frames[0])



    # choose plyer
    player_detections = player_tracker.choose_and_filter_players(court_keypoints, player_detections)

    # Mini court
    mini_court = MiniCourt(video_frames[0])

    # detect ball shorts
    ball_short_frames = ball_tracker.get_ball_shot_frames(ball_detections)
    print(ball_short_frames)


    # convert the posistion to mini court positions
    player_mini_court_detections, ball_mini_court_detections = mini_court.convert_bounding_boxes_to_mini_court_coordinates(player_detections, 
                                                                                                                           ball_detections, 
                                                                                                                           court_keypoints)


    output_video_frames = player_tracker.draw_bboxes(video_frames, player_detections)
    output_video_frames = ball_tracker.draw_bboxes(output_video_frames, ball_detections)

    output_video_frames = court_line_detector.draw_keypoints_on_video(output_video_frames, court_keypoints)

    # Drawing mini court 
    output_video_frames = mini_court.draw_mini_court(output_video_frames)
    output_video_frames = mini_court.draw_points_on_mini_court(output_video_frames, player_mini_court_detections )
    output_video_frames = mini_court.draw_points_on_mini_court(output_video_frames, ball_mini_court_detections, color=(0,255,255) )

    # Drawing frame count on top
    for i, frame in enumerate(output_video_frames):
        cv2.putText(frame, f"Frame: {i}", (10,30), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0,255,255), 2)

    save_video(output_video_frames, "output_videos/output_video.avi")

if __name__ == "__main__":
    main()