import pygame
from pygame.locals import *
import sys
from pygame.math import Vector2, Vector3
from matrix import Matrix
import objects_info.cube
from random import randint
from math import cos, pi, sin, radians, inf
import os.path

pathFile = os.path.dirname(__file__)

# Init pygame
pygame.init()
WIDTH = 800
HEIGHT = 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
FPS = 6000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
PURPLE = (127, 0, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 127, 0)

def map(n, start1, stop1, start2, stop2):
    return (n - start1) / (stop1 - start1) * (stop2 - start2) + start2

def clamp(n, minVal, maxVal):
    if n < minVal:
        return minVal
    elif n > maxVal:
        return maxVal
    return n

def drawText(text: str, pos: Vector2, fontSize: int=18, fontType: str="comicsans", bold: bool=False,
             italic: bool=False, antiAlias: bool=False, textColor: tuple=BLACK, bgColor: tuple=None,
             centerX: float=0, centerY: float=0, surface: pygame.Surface=window):
    font = pygame.font.SysFont(fontType, fontSize, bold, italic)
    textSurface = font.render(str(text), antiAlias, textColor, bgColor)
    textRect = textSurface.get_rect()
    surface.blit(textSurface, [pos.x + (textRect.width/2) * centerX, pos.y + (textRect.height/2) * centerY])

def sortMidpoints(zPoints: list):
  for i in range(len(zPoints)):
    for j in range(0, len(zPoints) - i - 1):
      if zPoints[j][1] < zPoints[j + 1][1]:
        temp = zPoints[j]
        zPoints[j] = zPoints[j+1]
        zPoints[j+1] = temp

class Face:
    def __init__(self, id: str, vertices: list[Vector2], color: tuple=BLACK) -> None:
        self.id: int = id
        self.vertices: list[Vector2] = vertices
        self.color: tuple = color

class BaseObject:
    def __init__(self, pos: Vector3, color: tuple=BLACK, edgeThickness: int=1,
                 cornerThickness: int=1, faces: list[int]=None, faceColors: dict=None, faceTextures: dict=None) -> None:
        self.pos = pos
        self.color = color
        self.edgeThickness = edgeThickness
        self.cornerThickness = cornerThickness
        self.rotation = Vector3(0, 0, 0)
        self.faces = faces or []
        self.faceColors: list[tuple] = faceColors or []
        self.faceTextures: list[pygame.Surface] = []
        if faceTextures:
            for faceId, spriteName in enumerate(faceTextures):
                self.faceTextures.append(pygame.image.load(os.path.join(pathFile, f"{spriteName}")).convert())
        self.size = 1
        self.points: list[Vector3] = []

    def rotateX(self, angle) -> None:
        self.rotation.x += radians(angle)

    def rotateY(self, angle) -> None:
        self.rotation.y += radians(angle)

    def rotateZ(self, angle) -> None:
        self.rotation.z += radians(angle)

    def getRotated(self) -> list[Matrix]:
        # Create rotation matrices
        rotationX: Matrix = Matrix([
            [1, 0, 0],
            [0, cos(self.rotation.x + radians(GLOBAL_ROTATION.x)), -sin(self.rotation.x + radians(GLOBAL_ROTATION.x))],
            [0, sin(self.rotation.x + radians(GLOBAL_ROTATION.x)),  cos(self.rotation.x + radians(GLOBAL_ROTATION.x))],
        ])
        rotationY: Matrix = Matrix([
            [cos(self.rotation.y + radians(GLOBAL_ROTATION.y)), 0, -sin(self.rotation.y + radians(GLOBAL_ROTATION.y))],
            [0, 1, 0],
            [sin(self.rotation.y + radians(GLOBAL_ROTATION.y)), 0, cos(self.rotation.y + radians(GLOBAL_ROTATION.y))],
        ])
        rotationZ: Matrix = Matrix([
            [cos(self.rotation.z + radians(GLOBAL_ROTATION.z)), -sin(self.rotation.z + radians(GLOBAL_ROTATION.z)), 0],
            [sin(self.rotation.z + radians(GLOBAL_ROTATION.z)),  cos(self.rotation.z + radians(GLOBAL_ROTATION.z)), 0],
            [0, 0, 1]
        ])

        # Save the projected points
        rotatedPoints: list[Matrix] = []

        # Calculate all vertex positions
        for point in self.points:
            # Rotate
            rotated = rotationX * Matrix.fromVector3(point)
            rotated = rotationY * rotated
            rotated = rotationZ * rotated

            rotatedPoints.append(rotated)

        return rotatedPoints

    def getPoints(self) -> list[Vector2]:

        # Save the projected points
        rotatedPoints = self.getRotated()
        projectedPoints: list = []

        # Calculate all vertex positions
        for point in rotatedPoints:
            # Calculate projected
            if orthographicProjection:
                z = 1
            else:
                try:
                    z = 1 / (GLOBAL_POSITION.z + point.toVector3().z)
                except ZeroDivisionError:
                    z = 1e-10

            projection: Matrix = Matrix([
                [z, 0, 0],
                [0, z, 0],
                [0, 0, z]
            ])
            # Add offset and scale
            projected = Matrix.toVector2(projection * point)
            pos = Vector2(self.pos.x + GLOBAL_POSITION.x + projected.x * self.size, self.pos.y + GLOBAL_POSITION.y + projected.y * self.size)
            projectedPoints.append(pos)
        
        return projectedPoints

    def draw(self, surface: pygame.Surface=window, drawEdges: bool=True, paintFaces: bool=False,
             drawTextures: bool=False) -> None:
        # Get points
        projectedPoints: list[Vector2] = self.getPoints()

        # Paint faces
        zPoints = []
        faces: list[Face] = []
        # Calculate color and vertices for each face
        for faceId, indexes in enumerate(self.faces):
            if len(indexes) == 0: continue

            # Try getting the color of the current face
            try:
                color = self.faceColors[faceId]
            except IndexError:
                print(f"No color for faceId {faceId}")
                continue

            rotatedPoints = self.getRotated()
            midPoint = Matrix.toVector3(rotatedPoints[indexes[0]]).lerp(Matrix.toVector3(rotatedPoints[indexes[2]]), .5)
            zPoints.append((faceId, midPoint.z))

            faceList: list = [projectedPoints[i] for i in indexes]
            
            faces.append(Face(faceId, faceList, color))

        # Sort mid points for correct face drawing
        sortMidpoints(zPoints)

        # Draw faces
        for f in zPoints:
            face: Face = None

            # Get face for given name
            for f1 in faces:
                if f1.id == f[0]:
                    face = f1
                    break

            # Draw face
            if paintFaces:
                pygame.draw.polygon(surface, face.color, face.vertices)

            # Draw texture
            textureSurface = None
            try:
                textureSurface: pygame.Surface = self.faceTextures[face.id]
                if not textureSurface and drawTextures:
                    continue
            except IndexError:
                pass
            if drawTextures and textureSurface:
                minX, maxX = WIDTH, 0
                minY, maxY = HEIGHT, 0
                for vertex in face.vertices:
                    if vertex.x < minX:
                        minX = vertex.x
                    if vertex.x > maxX:
                        maxX = vertex.x
                    if vertex.y < minY:
                        minY = vertex.y
                    if vertex.y > maxY:
                        maxY = vertex.y

                # Set size and scale texture
                size = Vector2(maxX - minX, maxY - minY)
                textureSurface = pygame.transform.scale(textureSurface, size)

                # Polygon surf
                polygonSurf = pygame.Surface(size, BLEND_RGBA_MAX).convert_alpha()
                polygonSurf.fill((255, 255, 255, 0))

                # Polygon mask
                pygame.draw.polygon(polygonSurf, BLACK, [(point.x - minX, point.y - minY) for point in face.vertices])
                polygonMask = pygame.mask.from_surface(polygonSurf)
                polygonMask.invert()
                newPolygonSurf = polygonMask.to_surface()
                newPolygonSurf.set_colorkey(BLACK)
                
                # Draw surfaces
                window.blit(textureSurface, (minX, minY))
                window.blit(newPolygonSurf, (minX, minY))

            # Draw outlines
            if drawEdges:
                pygame.draw.lines(surface, self.color, False, face.vertices, self.edgeThickness)

class Cube(BaseObject):
    def __init__(self, pos: Vector3=None, size: float=50, color: tuple=BLACK, edgeThickness: int=1,
                 cornerThickness: int=1, faceColors: dict=None, faceTextures: dict=None) -> None:
        super().__init__(pos, color, edgeThickness, cornerThickness, faceColors=faceColors, faceTextures=faceTextures)
        print(self.faceTextures)
        self.size = size
        self.points: list[Vector3] = objects_info.cube.vertices

    def draw(self, surface: pygame.Surface=window, drawEdges: bool=True, paintFaces: bool=False,
             drawTextures: bool=False) -> None:
        # Get points
        projectedPoints: list = self.getPoints()

        # Paint faces
        zPoints = []
        faces: list[Face] = []
        # Calculate color and vertices for each face
        for faceId, indexes in enumerate(objects_info.cube.faces):
            if len(indexes) == 0: continue
            color = self.faceColors[faceId]

            rotatedPoints = self.getRotated()
            # midPoint = sum([Matrix.toVector3(rotatedPoints[index]).z for index in indexes]) / len(indexes)
            midPoint = Matrix.toVector3(rotatedPoints[indexes[0]]).lerp(Matrix.toVector3(rotatedPoints[indexes[len(indexes)//2]]), .5).z
            zPoints.append((faceId, midPoint))

            faceList: list = [projectedPoints[i] for i in indexes]
            
            faces.append(Face(faceId, faceList, color))

        # Sort mid points for correct face drawing
        sortMidpoints(zPoints)

        # Draw faces
        for f in zPoints:
            face: Face = None

            # Get face for given name
            for f1 in faces:
                if f1.id == f[0]:
                    face = f1
                    break

            # Draw face
            if paintFaces:
                pygame.draw.polygon(surface, face.color, face.vertices)

            # Draw texture
            textureSurface = None
            try:
                textureSurface: pygame.Surface = self.faceTextures[face.id]
            except IndexError:
                pass
            if textureSurface and drawTextures:
                minX, maxX = WIDTH, 0
                minY, maxY = HEIGHT, 0
                for vertex in face.vertices:
                    if vertex.x < minX:
                        minX = vertex.x
                    if vertex.x > maxX:
                        maxX = vertex.x
                    if vertex.y < minY:
                        minY = vertex.y
                    if vertex.y > maxY:
                        maxY = vertex.y

                # Set size and scale texture
                size = Vector2(maxX - minX, maxY - minY)
                textureSurface = pygame.transform.scale(textureSurface, size)

                # Polygon surf
                polygonSurf = pygame.Surface(size, BLEND_RGBA_MAX | SRCALPHA).convert_alpha()
                polygonSurf.fill((0, 0, 0, 0))

                # Polygon mask
                pygame.draw.polygon(polygonSurf, BLACK, [(point.x - minX, point.y - minY) for point in face.vertices])
                polygonMask = pygame.mask.from_surface(polygonSurf)
                polygonMask.invert()
                newPolygonSurf = polygonMask.to_surface()
                newPolygonSurf.set_colorkey(BLACK)
                newPolygonSurf = newPolygonSurf.convert()
                
                # Draw surfaces
                window.blit(textureSurface, (minX, minY))
                window.blit(newPolygonSurf, (minX, minY))

            # Draw outlines
            if drawEdges:
                pygame.draw.lines(surface, self.color, False, face.vertices, self.edgeThickness)

class Sphere(BaseObject):
    def __init__(self, pos: Vector3=None, radius: float=50, resolution: int=15, color: tuple=BLACK, edgeThickness: int=1,
                 cornerThickness: int=1, faceColors: dict=None) -> None:
        super().__init__(pos, color, edgeThickness, cornerThickness, faceColors)
        self.size = radius
        self.radius = radius
        self.resolution = resolution

        # Calculate points
        for i in range(resolution):
            lat = map(i, 0, resolution-1, 0, 2*pi)
            for j in range(resolution):
                lon = map(j, 0, resolution-1, 0, pi)

                x = self.pos.x + sin(lon) * cos(lat)
                y = self.pos.y + sin(lon) * sin(lat)
                z = self.pos.z + cos(lon)
                self.points.append(Vector3(x, y, z))

        # Create faces
        self.faces: list[list[int]] = []
        for i in range(self.resolution-1):
            for j in range(self.resolution-1):
                i0 = i + j * self.resolution
                i1 = (i+1) + j * self.resolution
                i2 = i + (j+1) * self.resolution
                i3 = (i+1) + (j+1) * self.resolution
                self.faces.append([i0, i1, i3, i2, i0])

    def draw(self, surface: pygame.Surface=window, drawEdges: bool=True, paintFaces: bool=False,
             drawTextures: bool=False) -> None:
        # Get points
        projectedPoints = self.getPoints()
        rotatedPoints = self.getRotated()

        zPoints: list[tuple[int, float]] = []
        faces: list[Face] = []
        if paintFaces:
            for faceId, indexes in enumerate(self.faces):
                midPoint = Matrix.toVector3(rotatedPoints[indexes[0]]).lerp(Matrix.toVector3(rotatedPoints[indexes[2]]), .5)
                zPoints.append((faceId, midPoint.z))

                faceList: list = [projectedPoints[i] for i in indexes]
                
                color = pygame.Color(0, 0, 0)
                color.hsla = (faceId / len(self.faces) * 360, 100, 50)
                faces.append(Face(faceId, faceList, color))

        # Sort mid points for correct face drawing
        sortMidpoints(zPoints)

        # Draw faces
        for f in zPoints:
            face: Face = None

            # Get face for given name
            for f1 in faces:
                if f1.id == f[0]:
                    face = f1
                    break

            # Draw face
            if paintFaces:
                pygame.draw.polygon(surface, face.color, face.vertices)

            # Draw outlines
            if drawEdges:
                pygame.draw.lines(surface, self.color, False, face.vertices, self.edgeThickness)

        if drawEdges:
            for i in range(self.resolution-1):
                for j in range(self.resolution-1):
                    idx = i + j * self.resolution
                    idx1 = i + (j+1) * self.resolution
                    # Horizontal
                    pygame.draw.line(surface, BLACK, projectedPoints[idx], projectedPoints[idx1], self.edgeThickness)
                    # Vertical
                    pygame.draw.line(surface, BLACK, projectedPoints[idx], projectedPoints[idx+1], self.edgeThickness)

# Modes
orthographicProjection = False         # If false, Perspective Projection will be used
addRotation = False
addPosition = False
autoResetGlobalPosition = False
autoResetGlobalRotation = False

# Movement
GLOBAL_POSITION = Vector3(0, 0, 5)
GLOBAL_ROTATION = Vector3(0, 0, 0)
positionResetLerp = .005
rotationResetLerp = .002
positionAdd = Vector3(0, 0, 0)
rotationAdd = Vector3(0, 0, 0)
positionAddCapLerp = .003
rotationAddCapLerp = .001
zoomStep = .1

# Public methods for moving and rotating the scene
def translate(x: float, y: float, z: float) -> None:
    global GLOBAL_POSITION
    GLOBAL_POSITION += Vector3(x, y, z)

def rotateX(angle: float) -> None:
    global GLOBAL_ROTATION
    GLOBAL_ROTATION.x += angle

def rotateY(angle: float) -> None:
    global GLOBAL_ROTATION
    GLOBAL_ROTATION.y += angle

def rotateZ(angle: float) -> None:
    global GLOBAL_ROTATION
    GLOBAL_ROTATION.z += angle

def rotate(angleX: float, angleY: float, angleZ: float) -> None:
    global GLOBAL_ROTATION
    GLOBAL_ROTATION += Vector3(angleX, angleY, angleZ)

def changeZoom(diff: float) -> None:
    global GLOBAL_POSITION
    GLOBAL_POSITION.z = clamp(GLOBAL_POSITION.z - diff * zoomStep, 1, 1e10)

def main():
    global positionAdd, rotationAdd, GLOBAL_ROTATION, GLOBAL_POSITION
    # Objects
    objects: list[BaseObject] = []
    faceColors = [
        RED,
        GREEN,
        BLUE,
        WHITE,
        YELLOW,
        ORANGE,
    ]
    faceTextures = [
        "images/atumalaca.png",
        "images/atumalaca.png",
        "images/atumalaca.png",
        "images/atumalaca.png",
        "images/atumalaca.png",
        "images/atumalaca.png",
    ]
    lagartaTextures = [
        "images/lagarta.jpg",
        "images/lagarta.jpg",
        "images/lagarta.jpg",
        "images/lagarta.jpg",
        "images/lagarta.jpg",
        "images/lagarta.jpg",
    ]
    objects.append(Cube(Vector3(WIDTH/2, HEIGHT/2, 1), 400, BLACK, edgeThickness=2, faceColors=faceColors, faceTextures=lagartaTextures))
    #objects.append(Sphere(color=RED, pos=Vector3(0, 0, 3), radius=150, resolution=25, edgeThickness=1))

    # Import shape info
    import objects_info.shape

    # Create shape and change properties
    shapeObj = BaseObject(Vector3(WIDTH/2, HEIGHT/2, 0), color=BLACK, faces=objects_info.shape.faces)
    shapeObj.points = objects_info.shape.vertices
    shapeObj.size = 150
    shapeObj.faceColors = [
        RED,
        BLUE,
        BLACK,
        CYAN,
        YELLOW,
        PURPLE,
        GREEN,
        ORANGE
    ]

    # Add to list
    # objects.append(shapeObj)

    # Generate cube circle
    '''n = 100
    r = 150
    for i in range(n):
        faceColors = {
            "right": GREEN,
            "front": YELLOW,
            "back": BLUE,
            "top": BLACK,
            "bottom": ORANGE,
            "left": RED,
        }
        angle = map(i, 0, n, 0, 2*pi)
        x = WIDTH/2 + cos(angle - pi/2) * r
        y = HEIGHT/2 + sin(angle - pi/2) * r
        objects.append(Cube(pos=Vector3(x, y, 3), size=50, edgeThickness=1, faceColors=faceColors))
        #objects.append(Sphere(color=RED, pos=Vector3(x, y, 3), radius=150, resolution=3, edgeThickness=1, faceColors=faceColors))'''

    # States
    leftButtonDown = False
    rightButtonDown = False

    dt = 1000/FPS
    while True:
        mouseX = pygame.mouse.get_pos()[0]
        mouseY = pygame.mouse.get_pos()[1]
        mousePos = Vector2(mouseX, mouseY)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouseDown = True
            elif event.type == MOUSEBUTTONUP:
                mouseDown = False
            elif event.type == MOUSEWHEEL:
                GLOBAL_POSITION.z = clamp(GLOBAL_POSITION.z - event.y * zoomStep, 1, 1e10)
            elif event.type == MOUSEMOTION:
                if leftButtonDown:
                    # If left button is pressed, move position
                    positionAdd = Vector3(event.rel[0], event.rel[1], 0)
                    GLOBAL_POSITION += Vector3(event.rel[0], event.rel[1], 0)
                if rightButtonDown:
                    # If right button is pressed, rotate world
                    rotationAdd = Vector3(event.rel[1], -event.rel[0], 0)
                    GLOBAL_ROTATION += Vector3(event.rel[1], event.rel[0], 0)
            else:
                # Reset position and rotation adds
                positionAdd, rotationAdd = Vector3(0, 0, 0), Vector3(0, 0, 0)

        # Mouse input
        left, middle, right = pygame.mouse.get_pressed()
        leftButtonDown, rightButtonDown = left, right

        window.fill(WHITE)

        # Lerp global position and rotation offsets towards zero
        # Position
        if positionAdd.length_squared() < .01:
            positionAdd = Vector3(0, 0, 0)
        else:
            positionAdd = positionAdd.lerp(Vector3(0, 0, 0), positionAddCapLerp)
        # Rotation
        if rotationAdd.length_squared() < .01:
            rotationAdd = Vector3(0, 0, 0)
        else:
            rotationAdd = rotationAdd.lerp(Vector3(0, 0, 0), rotationAddCapLerp)

        # Add global position and rotation
        if addPosition and not autoResetGlobalPosition and not leftButtonDown and not rightButtonDown and positionAdd.length_squared() > 0:
            GLOBAL_POSITION += positionAdd * .1
        if addRotation and not autoResetGlobalRotation and not rightButtonDown and not leftButtonDown and rotationAdd.length_squared() > 0:
            GLOBAL_ROTATION += rotationAdd * .1

        # Reset global position and rotation
        if not leftButtonDown and autoResetGlobalPosition and GLOBAL_POSITION != Vector3(0, 0, 0):
            if GLOBAL_POSITION.length_squared() < 1:
                GLOBAL_POSITION = Vector3(0, 0, GLOBAL_POSITION.z)
            else:
                GLOBAL_POSITION = GLOBAL_POSITION.lerp(Vector3(0, 0, GLOBAL_POSITION.z), positionResetLerp)

        if not rightButtonDown and autoResetGlobalRotation and GLOBAL_ROTATION != Vector3(0, 0, 0):
            if GLOBAL_ROTATION.length_squared() < .5:
                GLOBAL_ROTATION = Vector3(0, 0, 0)
            else:
                GLOBAL_ROTATION = GLOBAL_ROTATION.lerp(Vector3(0, 0, 0), rotationResetLerp)

        # Draw objects
        for obj in objects:
            obj.draw(paintFaces=True, drawEdges=True, drawTextures=True)

        # Show FPS
        pygame.display.set_caption(f"3D Rendering | FPS: {clock.get_fps():.0f}")

        # Update screen
        pygame.display.update()
        clock.tick(FPS)

    '''
    TODO:
    - A esfera rotaciona ao redor de um outro ponto, e não em volta de si mesmo. nao faço ideia do q fazer todavia

    '''

# Movement
if __name__ == "__main__":
    main()