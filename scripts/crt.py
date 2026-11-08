import pygame
import moderngl
import struct

class CRT:

    def __init__(self, virtual_surface, shader_path='shaders/crt.glsl'):
        self.surface = virtual_surface
        self.ctx = moderngl.create_context()

        world = [-1, -1, 1, -1, -1, 1, 1, 1]
        uv = [0, 1, 1, 1, 0, 0, 1, 0]
        indices = [0, 1, 2, 1, 2, 3]

        self.prog = self.ctx.program(
            vertex_shader=open('shaders/vertex.glsl').read(),
            fragment_shader=open(shader_path).read())

        self.texture = self.ctx.texture(self.surface.get_size(), 3)
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        vbo = self.ctx.buffer(struct.pack('8f', *world))
        uvmap = self.ctx.buffer(struct.pack('8f', *uv))
        ibo = self.ctx.buffer(struct.pack('6I', *indices))
        self.vao = self.ctx.vertex_array(self.prog, [(vbo, '2f', 'vert'), (uvmap, '2f', 'in_text')], ibo)

    def render(self):
        self.texture.write(self.surface.get_view('1'))
        self.ctx.clear(0,0, 0)
        self.texture.use()
        self.vao.render()
        pygame.display.flip()