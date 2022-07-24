from pygame.math import Vector3

vertices: list[Vector3] = [
    Vector3(-4, -1, -1.5),
    Vector3(-4, 1, -1.5),
    Vector3(-3, 1, -1.5),
    Vector3(-3, 0, -1.5),
    Vector3(3, 0, -1.5),
    Vector3(3, 1, -1.5),
    Vector3(4, 1, -1.5),
    Vector3(4, -1, -1.5),

    Vector3(4, -1, 1.5),
    Vector3(4, 1, 1.5),
    Vector3(3, 1, 1.5),
    Vector3(3, 0, 1.5),
    Vector3(-3, 0, 1.5),
    Vector3(-3, 1, 1.5),
    Vector3(-4, 1, 1.5),
    Vector3(-4, -1, 1.5),
]

faces: list[int] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 0],
    [8, 9, 10, 11, 12, 13, 14, 15, 8],
    [0, 7, 8, 15, 0],
    [0, 1, 14, 15, 0],
    [6, 5, 10, 9, 6],
    [2, 3, 12, 13, 2],
    [4, 5, 10, 11, 4],
    [3, 4, 11, 12, 3]
]