from PIL import Image, ImageDraw
import os
import json
import numpy as np
from hashlib import md5
import shutil

TILE_SIZE = 32
INPUT_IMAGE = "level1.png"
OUTPUT_DIR = "output/tiles/"
TILEMAP_PATH = "output/tilemap.json"
METADATA_PATH = "output/metadata.json"
VISUALIZATION_PATH = "output/visualization.png"

# Flag to enable perceptual similarity instead of exact matching
USE_PERCEPTUAL_MATCHING = True
# Tolerance for pixel differences (0-255)
SIMILARITY_THRESHOLD = 5


def get_tile_signature(tile, perceptual=USE_PERCEPTUAL_MATCHING):
    """
    Generate a signature for a tile for comparison purposes

    If perceptual=True, use a more forgiving comparison that ignores minor differences
    """
    if not perceptual:
        # Exact matching - use MD5 hash
        tile_data = np.array(tile)
        return md5(tile_data.tobytes()).hexdigest()
    else:
        # Perceptual matching - downsample and quantize colors
        small_tile = tile.resize((8, 8), Image.LANCZOS)  # Downsample to 8x8

        # Convert to numpy array for manipulation
        arr = np.array(small_tile)

        # Quantize color values to reduce sensitivity to minor variations
        arr = (arr // SIMILARITY_THRESHOLD) * SIMILARITY_THRESHOLD

        # Create a hash of this simplified representation
        return md5(arr.tobytes()).hexdigest()


def are_tiles_similar(tile1, tile2, threshold=SIMILARITY_THRESHOLD):
    """Check if tiles are visually similar by calculating pixel differences"""
    if not USE_PERCEPTUAL_MATCHING:
        return False  # Skip this check if not using perceptual matching

    # Convert to numpy arrays
    arr1 = np.array(tile1)
    arr2 = np.array(tile2)

    # Calculate mean absolute difference between tiles
    diff = np.abs(arr1.astype(np.int16) - arr2.astype(np.int16))
    mean_diff = np.mean(diff)

    # Tiles are similar if the average difference is below threshold
    return mean_diff < threshold


def find_similar_tile(tile, unique_tiles, tile_hashes):
    """
    Find an existing tile that's similar enough to the current one
    Returns the index of a similar tile, or None if no match
    """
    # First check using the faster hash method
    tile_sig = get_tile_signature(tile)
    if tile_sig in tile_hashes:
        return tile_hashes[tile_sig]

    # If perceptual matching is enabled, do a more thorough check
    if USE_PERCEPTUAL_MATCHING:
        for idx, existing_tile in enumerate(unique_tiles):
            if are_tiles_similar(tile, existing_tile):
                # Add this signature to the hash map to speed up future lookups
                tile_hashes[tile_sig] = idx
                return idx

    return None


def visualize_tilemap(image, tilemap, unique_count, output_path):
    """Create a visualization showing which tiles are duplicates"""
    # Create a copy of the original image
    vis_img = image.copy()
    draw = ImageDraw.Draw(vis_img)

    # Assign colors to unique tile IDs (cycling through a rainbow for visibility)
    colors = []
    for i in range(unique_count):
        # Generate a color based on the tile index
        hue = (i * 137) % 360  # Use golden angle to spread colors

        # Convert HSV to RGB (simplified - not perfect but good enough for visualization)
        h = hue / 60
        sector = int(h)
        f = h - sector

        p = 0
        q = int(255 * (1 - f))
        t = int(255 * f)
        v = 255

        if sector == 0:
            r, g, b = v, t, p
        elif sector == 1:
            r, g, b = q, v, p
        elif sector == 2:
            r, g, b = p, v, t
        elif sector == 3:
            r, g, b = p, q, v
        elif sector == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        colors.append((r, g, b, 128))  # Semi-transparent

    # Draw grid and color each cell based on its tile ID
    width, height = image.size
    for y in range(len(tilemap)):
        for x in range(len(tilemap[y])):
            tile_id = tilemap[y][x]
            color = colors[tile_id % len(colors)]

            # Draw a colored rectangle
            draw.rectangle(
                [
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    (x + 1) * TILE_SIZE - 1,
                    (y + 1) * TILE_SIZE - 1,
                ],
                outline=(0, 0, 0, 255),
                fill=color,
            )

            # Add the tile ID number
            draw.text(
                (x * TILE_SIZE + 2, y * TILE_SIZE + 2),
                str(tile_id),
                fill=(255, 255, 255, 200),
            )

    # Save the visualization
    vis_img.save(output_path)
    print(f"Visualization saved to {output_path}")


def main():
    # Clean output directory if it exists
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load and process the image
    img = Image.open(INPUT_IMAGE).convert("RGBA")
    width, height = img.size

    # Print initial info
    print(f"Image size: {width}x{height}")
    print(f"Using {TILE_SIZE}x{TILE_SIZE} tiles")
    print(f"Perceptual matching: {'ON' if USE_PERCEPTUAL_MATCHING else 'OFF'}")
    if USE_PERCEPTUAL_MATCHING:
        print(f"Similarity threshold: {SIMILARITY_THRESHOLD}")

    # Collections to store tiles and mappings
    unique_tiles = []  # The actual tile images
    tile_hashes = {}  # Mapping from tile signature to index
    tilemap = []  # 2D grid of tile indices

    # Statistics
    total_tiles = 0
    duplicates_found = 0

    # Process the image tile by tile
    for y in range(0, height, TILE_SIZE):
        row = []
        for x in range(0, width, TILE_SIZE):
            total_tiles += 1

            # Extract the current tile
            tile = img.crop((x, y, x + TILE_SIZE, y + TILE_SIZE))

            # Try to find a match among existing tiles
            similar_idx = find_similar_tile(tile, unique_tiles, tile_hashes)

            if similar_idx is not None:
                # We found a similar tile - use its index
                row.append(similar_idx)
                duplicates_found += 1
            else:
                # This is a new unique tile
                new_idx = len(unique_tiles)
                unique_tiles.append(tile)

                # Add it to our hash map
                tile_sig = get_tile_signature(tile)
                tile_hashes[tile_sig] = new_idx

                # Save the tile image
                tile.save(f"{OUTPUT_DIR}tile_{new_idx:03d}.png")

                # Add to tilemap
                row.append(new_idx)

        tilemap.append(row)

    # Calculate stats and compression ratio
    unique_count = len(unique_tiles)
    compression = (
        (total_tiles - unique_count) / total_tiles * 100 if total_tiles > 0 else 0
    )

    # Save the tilemap
    with open(TILEMAP_PATH, "w") as f:
        json.dump(tilemap, f, indent=2)

    # Save metadata
    metadata = {
        "image_size": f"{width}x{height}",
        "tile_size": TILE_SIZE,
        "grid_size": f"{width//TILE_SIZE}x{height//TILE_SIZE}",
        "total_tiles": total_tiles,
        "unique_tiles": unique_count,
        "duplicates_found": duplicates_found,
        "compression_ratio": f"{compression:.2f}%",
        "perceptual_matching": USE_PERCEPTUAL_MATCHING,
        "similarity_threshold": SIMILARITY_THRESHOLD,
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    # Create a visualization
    visualize_tilemap(img, tilemap, unique_count, VISUALIZATION_PATH)

    # Print summary
    print("\n===== Results =====")
    print(f"Total tiles processed: {total_tiles}")
    print(f"Unique tiles found: {unique_count}")
    print(f"Duplicates found: {duplicates_found}")
    print(f"Compression ratio: {compression:.2f}%")
    print(f"Tilemap saved to: {TILEMAP_PATH}")
    print(f"Tiles saved to: {OUTPUT_DIR}")
    print(f"Visualization saved to: {VISUALIZATION_PATH}")


if __name__ == "__main__":
    main()
