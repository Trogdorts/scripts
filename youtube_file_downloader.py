import re
import os
import argparse
from pytube import YouTube
from pytube.exceptions import RegexMatchError

def is_writable_directory(path):
    try:
        test_file = os.path.join(path, "__writable_test__")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except Exception:
        return False

def download_youtube_videos(links_file, output_directory, verbose_level, redownload):

    existing_video_files = []
    for filename in os.listdir(output_directory):
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')):
            base_name, _ = os.path.splitext(filename)
            existing_video_files.append(base_name)


    if not is_writable_directory(output_directory):
        print(f"Error: Output directory '{output_directory}' is not writable.")
        return

    # Regular expression pattern to match YouTube links
    youtube_pattern = r"https://www\.youtube\.com/watch\?v=[\w-]+"

    # Counter for numbering the videos
    video_number = 0

    with open(links_file, "r") as file:
        content = file.readlines()

    for line in content:
        youtube_links = re.findall(youtube_pattern, line)
        for link in youtube_links:
            try:
                yt = YouTube(link)

                # Choose a stream with the MKV format
                video = yt.streams.filter(file_extension="mkv").first()
                if not video:
                    # Choose a stream with the MP4 format
                    video = yt.streams.filter(file_extension="mp4").first()

                if video:
                    video_number += 1

                    # Prepend the number to the video title
                    video_title = f"{video_number:02d}_{yt.title}"

                    # Check if the video title has been downloaded before
                    if video_title in existing_video_files and not redownload:
                        if verbose_level >= 1:
                            print(f"{video_title} already downloaded. Skipping.")
                    else:
                        if verbose_level >= 1:
                            print(f"Downloading {video_title}")

                        # Modify the filename to include the video number
                        filename = f"{video_number:02d}_{video.default_filename}"

                        # Download the video with the modified filename
                        video.download(output_path=output_directory, filename=filename)

                        if verbose_level >= 1:
                            print(f"{video_title} downloaded successfully.")


                else:
                    if verbose_level >= 2:
                        print(f"No MKV or MP4 format available for {yt.title}")
            except (RegexMatchError, Exception) as e:
                if verbose_level >= 2:
                    print(f"Error downloading {link}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos from links in a text file.")
    parser.add_argument("links_file", help="Path to the text file containing YouTube links.")
    parser.add_argument("-o", "--save-directory", default=".", help="Directory where the videos will be saved. Default is the current directory.")
    parser.add_argument("-v", "--verbose", action="count", default=1, help="Increase verbosity level. Use -v, -vv, or -vvv.")
    parser.add_argument("--redownload", action="store_true", help="Redownload videos that already exist in the directory.")
    args = parser.parse_args()

    if not os.path.exists(args.save_directory):
        os.makedirs(args.save_directory)

    download_youtube_videos(args.links_file, args.save_directory, args.verbose, args.redownload)

if __name__ == "__main__":
    main()