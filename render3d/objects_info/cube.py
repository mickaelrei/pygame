from pygame.math import Vector3

vertices: list[Vector3] = [
    # Back
    Vector3(-1, -1, -1),
    Vector3(1, -1, -1),
    Vector3(1, 1, -1),
    Vector3(-1, 1, -1),

    # Front
    Vector3(-1, -1, 1),
    Vector3(1, -1, 1),
    Vector3(1, 1, 1),
    Vector3(-1, 1, 1),
]

faces: list[int] = [
    [0, 3, 7, 4, 0],
    [1, 2, 6, 5, 1],
    [4, 5, 6, 7, 4],
    [0, 1, 2, 3, 0],
    [4, 0, 1, 5, 4],
    [7, 3, 2, 6, 7]
]