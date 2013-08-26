#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2010 Santhosh Thottingal <santhosh.thottingal@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os
import cairo
import hashlib
import pango
import pangocairo
import hyphenation
from wiki2pdf import Wikiparser
from styles import *


class Render:
    def __init__(self):
        self.tmp_folder = "/static/tmp"

    def wiki2pdf(self, url, font='Serif'):
        m = hashlib.md5()
        m.update(url.encode("utf-8"))
        filename = m.hexdigest()[0:5]+".pdf"
        #if not os.path.exists(os.path.join(os.path.dirname(__file__), "tmp",filename)):
        parser = Wikiparser(url, filename, font)
        parser.parse()
        #else:
        #	print ("File already exists.")
        return (os.path.join(self.tmp_folder, filename))

    def render_text(self, text, file_type='png', width=0,
                    height=0, color="Black", font='Serif', font_size=12):
        surface = None
        width = int(width)
        height = int(height)
        font_size = int(font_size)
        text = text.decode("utf-8")
        m = hashlib.md5()
        m.update(text.encode("utf-8"))
        filename = m.hexdigest()[0:5]+"."+file_type
        outputfile = os.path.join(os.getcwd(),"static","tmp", filename)
        if file_type == 'png':
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                         int(width), int(height))
        if file_type == 'svg':
            surface = cairo.SVGSurface(outputfile,
                                       int(width), int(height))
        if file_type == 'pdf':
            surface = cairo.PDFSurface(outputfile, int(width), int(height))
        context = cairo.Context(surface)
        try:
            text = hyphenation.getInstance().hyphenate(text, u'\u00AD')
        except:
            print("error while hyphenating. Proceeding without Hyphenation")
        width = int(width)
        left_margin = 10
        top_margin = 20
        bottom_margin = 50
        position_x = left_margin
        position_y = top_margin
        rgba = get_color(color)
        context.set_source_rgba(float(rgba.red), float(rgba.green),
                                float(rgba.blue), float(rgba.alpha))
        pc = pangocairo.CairoContext(context)
        paragraph_layout = pc.create_layout()
        paragraph_font_description = pango.FontDescription()
        paragraph_font_description.set_family(font)
        paragraph_font_description.set_size((int)(int(font_size) *
                                                  pango.SCALE))
        paragraph_layout.set_font_description(paragraph_font_description)
        if width > 0:
            paragraph_layout.set_width((int)((width-2*left_margin) *
                                             pango.SCALE))
            paragraph_layout.set_justify(True)
        paragraph_layout.set_text(text+"\n")
        context.move_to(position_x, position_y)
        pango_layout_iter = paragraph_layout.get_iter()

        line_width = 0
        while not pango_layout_iter.at_last_line():
            first_line = True
            context.move_to(position_x, position_y)
            while not pango_layout_iter.at_last_line():
                ink_rect, logical_rect = pango_layout_iter.get_line_extents()
                line = pango_layout_iter.get_line_readonly()
                has_next_line = pango_layout_iter.next_line()
                # Decrease paragraph spacing
                if ink_rect[2] == 0:      # It is para break
                    dy = font_size / 2
                    position_y += dy
                    if not first_line:
                        self.context.rel_move_to(0, dy)
                else:
                    xstart = 1.0 * logical_rect[0] / pango.SCALE
                    context.rel_move_to(xstart, 0)
                    if width > 0 and height > 0:
                        pc.show_layout_line(line)
                    line_height = (int)(logical_rect[3] / pango.SCALE)
                    line_width = (int)(logical_rect[2] / pango.SCALE)
                    context.rel_move_to(-xstart, line_height)
                    position_y += line_height
            first_line = False
        if width == 0 or height == 0:
            if width == 0:
                width = line_width
            if height == 0:
                height = position_y
            return self.render_text(text, file_type, width + 2.5*left_margin,
                                    height, color, font, font_size)
        if file_type == 'png':
            surface.write_to_png(str(outputfile))
        else:
            context.show_page()
        return "/static/tmp/"+filename

    def get_module_name(self):
        return "Script Renderer"

    def get_info(self):
        return "Provides rendered images for Complex scripts"


def getInstance():
    return Render()
