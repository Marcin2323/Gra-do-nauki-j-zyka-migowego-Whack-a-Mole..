import pygame
import moviepy.editor as mp

def load_image(path, size=None):
    image = pygame.image.load(path)
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_gif_frames(path):
    clip = mp.VideoFileClip(path)
    fps = clip.fps
    gif_duration = clip.duration
    clip_duration = int(gif_duration * fps)
    gif_frames = [pygame.image.frombuffer(clip.get_frame(i / fps / 2).tobytes(), clip.size, 'RGB') for i in range(clip_duration)]
    return gif_frames, clip_duration
