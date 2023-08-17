from pygame.math import Vector3

def readObj(filePath: str) -> tuple[list[Vector3], list[list[int]]]:
    '''
    Receives file path, reads file content and returns list of vertices and list of face indexes'''

    vertices: list[Vector3] = []
    faces: list[list[int]] = []

    # Read file
    with open(filePath, 'r') as f:
        content: list[str] = f.readlines()

    # Read all lines
    for line in content:
        line = line.replace('\n', '')

        # Check for initials
        split = line.split(" ")
        if split[0] == 'v':
            vertices.append(Vector3(float(split[1]), float(split[2]), float(split[3])))
        elif split[0] == 'f':
            indexes = []

            for info in split[1:]:
                idx = info.split("/")[0]
                indexes.append(int(idx) - 1)

            faces.append(indexes)

            # i0 = split[1].split('/')[0]
            # i1 = split[2].split('/')[0]
            # i2 = split[3].split('/')[0]

            # faces.append((int(i0) - 1, int(i1) - 1, int(i2) - 1))

    print(f"Vertices: {len(vertices)}")
    print(f"Faces: {len(faces)}")

    return vertices, faces

if __name__ == "__main__":
    import os.path

    file = 'ico_sphere.obj'
    filePath = os.path.join(__file__, f'../{file}')
    
    readObj(filePath)