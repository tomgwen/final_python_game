from hex_map import HexMap

def initialize_fog(hex_map: HexMap, start_position: tuple[int, int]) -> None:
    reveal_around(hex_map, start_position)

def reveal_around(hex_map: HexMap, position: tuple[int, int]) -> list[tuple[int, int]]:
    revealed_positions = []
    q, r = position
    
    # Reveal current position
    current_tile = hex_map.get_tile(q, r)
    if current_tile:
        current_tile.discovered = True
        revealed_positions.append((q, r))
        
    # Reveal valid neighbors
    for nq, nr in hex_map.get_neighbors(q, r):
        neighbor_tile = hex_map.get_tile(nq, nr)
        if neighbor_tile:
            neighbor_tile.discovered = True
            revealed_positions.append((nq, nr))
            
    return revealed_positions