import re
import sys

def update_m3u_urls(layout_file_path, stream_links_file_path, output_file_path):
    """
    Updates stream URLs in a M3U playlist based on a separate file containing new links.

    Args:
        layout_file_path (str): Path to the M3U file containing the layout (e.g., moveonjoy pigz.txt).
        stream_links_file_path (str): Path to the M3U file containing updated stream links (e.g., us_moveonjoy iptvorg.txt).
        output_file_path (str): Path where the updated M3U content will be saved.
    """

    # Read the new stream links and map tvg-id to URL
    tvg_id_to_url = {}
    with open(stream_links_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
            if tvg_id_match:
                tvg_id = tvg_id_match.group(1)
                # The next line should be the URL
                if i + 1 < len(lines):
                    url = lines[i+1].strip()
                    if url.startswith('http'):
                        if tvg_id not in tvg_id_to_url: # Only take the first URL if duplicates exist
                            tvg_id_to_url[tvg_id] = url
                i += 1 # Move to the next line after the URL
        i += 1


    # Read the layout file and update URLs
    updated_lines = []
    with open(layout_file_path, 'r', encoding='utf-8') as f:
        layout_lines = f.readlines()

    j = 0
    while j < len(layout_lines):
        line = layout_lines[j].strip()
        updated_lines.append(layout_lines[j]) # Always add the current line

        if line.startswith('#EXTINF:'):
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
            if tvg_id_match:
                tvg_id = tvg_id_match.group(1)
                if tvg_id in tvg_id_to_url:
                    # Replace the next line (URL) with the new URL
                    if j + 1 < len(layout_lines) and layout_lines[j+1].strip().startswith('http'):
                        updated_lines.append(tvg_id_to_url[tvg_id] + '\n')
                        j += 1 # Skip the original URL line as we've replaced it
        j += 1

    # Write the updated content to the output file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_m3u.py <layout_file_path> <stream_links_file_path> <output_file_path>")
        sys.exit(1)

    layout_file = sys.argv[1]
    stream_links_file = sys.argv[2]
    output_file = sys.argv[3]

    update_m3u_urls(layout_file, stream_links_file, output_file)
    print(f"Successfully updated M3U and saved to {output_file}")
