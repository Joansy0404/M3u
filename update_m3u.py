import re
import sys

def update_m3u_urls(layout_file_path, stream_links_file_path, output_file_path):
    """
    Updates stream URLs in a M3U playlist based on a separate file containing new links.

    Args:
        layout_file_path (str): Path to the M3U file containing the layout.
        stream_links_file_path (str): Path to the M3U file containing updated stream links.
        output_file_path (str): Path where the updated M3U content will be saved.
    """

    print(f"--- Starting M3U Update ---")
    print(f"Layout file: {layout_file_path}")
    print(f"Stream links file: {stream_links_file_path}")
    print(f"Output file: {output_file_path}")

    tvg_id_to_url = {}
    print("\n--- Processing Stream Links File ---")
    try:
        with open(stream_links_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"Read {len(lines)} lines from stream links file.")
    except Exception as e:
        print(f"Error reading stream links file: {e}")
        sys.exit(1)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
            if tvg_id_match:
                tvg_id = tvg_id_match.group(1)
                if i + 1 < len(lines):
                    url = lines[i+1].strip()
                    if url.startswith('http'):
                        if tvg_id not in tvg_id_to_url:
                            tvg_id_to_url[tvg_id] = url
                        i += 1
                else:
                    print(f"  [WARNING] #EXTINF line without subsequent URL at line {i+1} in stream links file: {line}")
            else:
                print(f"  [WARNING] #EXTINF line without tvg-id in stream links file: {line}")
        i += 1
    print(f"Finished processing stream links file. Mapped {len(tvg_id_to_url)} unique tvg-ids.")


    updated_lines = []
    print("\n--- Processing Layout File ---")
    try:
        with open(layout_file_path, 'r', encoding='utf-8') as f:
            layout_lines = f.readlines()
        print(f"Read {len(layout_lines)} lines from layout file.")
    except Exception as e:
        print(f"Error reading layout file: {e}")
        sys.exit(1)

    j = 0
    match_count = 0
    while j < len(layout_lines):
        current_layout_line = layout_lines[j]
        updated_lines.append(current_layout_line)

        line_stripped = current_layout_line.strip()
        if line_stripped.startswith('#EXTINF:'):
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line_stripped)
            if tvg_id_match:
                tvg_id = tvg_id_match.group(1)
                if tvg_id in tvg_id_to_url:
                    if j + 1 < len(layout_lines) and layout_lines[j+1].strip().startswith('http'):
                        new_url = tvg_id_to_url[tvg_id] + '\n'
                        updated_lines.append(new_url)
                        j += 1
                        match_count += 1
                    else:
                        print(f"  [WARNING] #EXTINF line without subsequent URL in layout file at line {j+1}: {line_stripped}")
        j += 1
    print(f"Finished processing layout file. Found {match_count} tvg-id matches and replacements.")

    print(f"\n--- Writing Output File ({output_file_path}) ---")
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print(f"Successfully wrote {len(updated_lines)} lines to {output_file_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    print("--- M3U Update Script Finished ---")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python update_m3u.py <layout_file_path> <stream_links_file_path> <output_file_path>")
        sys.exit(1)

    layout_file = sys.argv[1]
    stream_links_file = sys.argv[2]
    output_file = sys.argv[3]

    update_m3u_urls(layout_file, stream_links_file, output_file)
