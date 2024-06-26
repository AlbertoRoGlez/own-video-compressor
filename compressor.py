import os, ffmpeg, glob
def compress_video(video_full_path, target_size):
    # Reference: https://en.wikipedia.org/wiki/Bit_rate#Encoding_bit_rate
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    target_size = target_size*1000

    # Remove the file extension from the input video file path
    video_path_without_extension, _ = os.path.splitext(video_full_path)

    # Create the output file name
    file_name = os.path.basename(video_path_without_extension)
    output_file_name = f"{file_name}-compressed-{target_size/1000}MB.mp4"

    # Create output path
    directory_path = os.path.dirname(video_full_path)
    output_folder = os.path.join(directory_path, "CompressedVideos")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Directory 'CompressedVideos' created successfully at {directory_path}")
    else:
        print(f"Directory 'CompressedVideos' already exists at {directory_path}")

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    # Target total bitrate, in bps.
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'av1_nvenc', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()

    ffmpeg.output(i, f"{output_folder}/{output_file_name}",
                  **{'c:v': 'av1_nvenc', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

# Compress input.mp4 to 25MB

def compress_all_in_path(path):
    path = f"{path}/*"
    files = glob.glob(path)
    # Loop through each file
    for file in files:
    # Split the file name and extension
        root, ext = os.path.splitext(file)
        # Check if the file extension is a common video extension
        if ext.lower() in ['.mov','.mp4','.m4a','.3gp','.3g2','.mj2']:
            # Perform your desired operations on the file
            print(file)
            compress_video(file, 25)
    # Find and delete the log files generated by ffmpeg
    for file in os.listdir("."):
        root, ext = os.path.splitext(file)
        if ext.lower() in ['.log','.mbtree','.log.mbtree']:
            os.remove(file)

def get_path_from_cmd():
    return input("Please enter the path folder of videos to compress: ")

if __name__ == "__main__":
    path = get_path_from_cmd()
    compress_all_in_path(path)