#!/usr/bin/env python3
"""
Tower of Hanoi — Visual Solver
A pygame GUI wrapping the original closed-form (non-recursive) Hanoi solver.

Reuses, unmodified, the original project's logic:
    - calculate_solution.py  (compute_full_sequence, compute_move_transition)
    - utils.py                (validation, save/load/verify solutions)
    - problems.json            (50 preset problems)

All three original input methods are supported (Classic, Custom, Presets),
plus solution saving/verifying, wrapped in a smooth animated GUI.
"""

import sys
import os
import math
import json
import pygame

from calculate_solution import compute_full_sequence
from utils import is_valid_rods_state, save_solution, load_solution, verify_solution

# ----------------------------------------------------------------------------
# Constants & Theme
# ----------------------------------------------------------------------------

SCREEN_W, SCREEN_H = 1200, 780
MIN_SCREEN_W, MIN_SCREEN_H = 860, 600
FPS = 60

# Palette — warm dark background, wood-toned base, gem-toned rings
BG_TOP = (20, 24, 38)
BG_BOTTOM = (34, 30, 54)
PANEL_BG = (30, 34, 52)
PANEL_BG_LIGHT = (40, 45, 66)
PANEL_BORDER = (70, 76, 104)
ACCENT = (124, 154, 255)
ACCENT_DIM = (78, 92, 150)
ACCENT_2 = (255, 176, 89)
TEXT_MAIN = (232, 235, 245)
TEXT_DIM = (150, 156, 180)
TEXT_FAINT = (100, 106, 130)
SUCCESS = (108, 219, 148)
ERROR = (240, 100, 110)
WOOD_DARK = (76, 52, 40)
WOOD_LIGHT = (112, 78, 56)
ROD_COLOR = (150, 110, 70)
ROD_HIGHLIGHT = (190, 148, 100)

RING_PALETTE = [
    (239, 83, 80),  # red
    (255, 152, 60),  # orange
    (255, 202, 58),  # yellow
    (129, 212, 111),  # green
    (77, 208, 199),  # teal
    (79, 172, 235),  # blue
    (146, 130, 240),  # purple
    (236, 121, 194),  # pink
    (161, 136, 127),  # brown
    (176, 190, 197),  # grey-blue
    (255, 111, 97),  # coral
    (100, 221, 178),  # mint
]

FONT_NAME = None  # default system font


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    p = 2 * t - 2
    return 0.5 * p * p * p + 1


def ease_out_back(t, overshoot=1.4):
    t = t - 1
    return t * t * ((overshoot + 1) * t + overshoot) + 1


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def vertical_gradient(surface, top_color, bottom_color):
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        t = y / max(1, h - 1)
        color = (
            int(lerp(top_color[0], bottom_color[0], t)),
            int(lerp(top_color[1], bottom_color[1], t)),
            int(lerp(top_color[2], bottom_color[2], t)),
        )
        pygame.draw.line(surface, color, (0, y), (w, y))


def rounded_rect(
    surface, rect, color, radius=10, width=0, border_color=None, border_width=0
):
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(
            surface, border_color, rect, width=border_width, border_radius=radius
        )


def shade(color, factor):
    """factor > 1 lightens, < 1 darkens"""
    return tuple(clamp(int(c * factor), 0, 255) for c in color)


# ----------------------------------------------------------------------------
# Button widget
# ----------------------------------------------------------------------------


class Button:
    def __init__(
        self,
        rect,
        label,
        font,
        on_click=None,
        style="primary",
        enabled=True,
        subtitle=None,
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.on_click = on_click
        self.style = style  # primary, secondary, ghost, danger
        self.enabled = enabled
        self.hovered = False
        self.subtitle = subtitle
        self._press_anim = 0.0

    def handle_event(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._press_anim = 1.0
                if self.on_click:
                    self.on_click()

    def update(self, dt):
        self._press_anim = max(0.0, self._press_anim - dt * 4)

    def draw(self, surf):
        r = self.rect.copy()
        press_offset = int(self._press_anim * 2)
        r.y += press_offset

        if not self.enabled:
            bg = (46, 48, 60)
            border = (60, 62, 76)
            text_color = TEXT_FAINT
        elif self.style == "primary":
            bg = shade(ACCENT, 1.12) if self.hovered else ACCENT
            border = shade(ACCENT, 1.4)
            text_color = (18, 20, 30)
        elif self.style == "danger":
            bg = shade(ERROR, 1.1) if self.hovered else ERROR
            border = shade(ERROR, 1.3)
            text_color = (30, 12, 14)
        elif self.style == "secondary":
            bg = PANEL_BG_LIGHT if self.hovered else PANEL_BG
            border = ACCENT_DIM if self.hovered else PANEL_BORDER
            text_color = TEXT_MAIN
        else:  # ghost
            bg = (255, 255, 255, 0)
            border = PANEL_BORDER if not self.hovered else ACCENT_DIM
            text_color = TEXT_DIM if not self.hovered else TEXT_MAIN

        if self.style != "ghost":
            rounded_rect(surf, r, bg, radius=12, border_color=border, border_width=2)
        else:
            rounded_rect(
                surf, r, PANEL_BG, radius=12, border_color=border, border_width=2
            )

        if self.subtitle:
            label_surf = self.font.render(self.label, True, text_color)
            sub_font = pygame.font.Font(FONT_NAME, max(24, self.font.get_height() - 10))
            sub_surf = sub_font.render(
                self.subtitle,
                True,
                shade(text_color, 0.75) if self.enabled else text_color,
            )
            total_h = label_surf.get_height() + sub_surf.get_height() + 2
            ly = r.centery - total_h // 2
            surf.blit(label_surf, label_surf.get_rect(centerx=r.centerx, top=ly))
            surf.blit(
                sub_surf,
                sub_surf.get_rect(
                    centerx=r.centerx, top=ly + label_surf.get_height() + 2
                ),
            )
        else:
            label_surf = self.font.render(self.label, True, text_color)
            surf.blit(label_surf, label_surf.get_rect(center=r.center))


class TextInput:
    """A minimal single-line text input box."""

    def __init__(self, rect, font, placeholder="", numeric=False, initial=""):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.placeholder = placeholder
        self.text = initial
        self.active = False
        self.numeric = numeric
        self.cursor_timer = 0.0
        self.cursor_visible = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_TAB, pygame.K_KP_ENTER):
                pass
            else:
                ch = event.unicode
                if ch:
                    if self.numeric:
                        if (
                            ch.isdigit()
                            or (ch in "," and "," not in self.text[-1:])
                            or ch == " "
                        ):
                            if len(self.text) < 60:
                                self.text += ch
                    else:
                        if ch.isprintable() and len(self.text) < 60:
                            self.text += ch

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surf):
        bg = PANEL_BG_LIGHT if self.active else PANEL_BG
        border = ACCENT if self.active else PANEL_BORDER
        rounded_rect(surf, self.rect, bg, radius=8, border_color=border, border_width=2)
        if self.text:
            txt_surf = self.font.render(self.text, True, TEXT_MAIN)
        else:
            txt_surf = self.font.render(self.placeholder, True, TEXT_FAINT)
        surf.blit(
            txt_surf, (self.rect.x + 12, self.rect.centery - txt_surf.get_height() // 2)
        )
        if self.active and self.cursor_visible:
            cx = (
                self.rect.x
                + 12
                + (self.font.size(self.text)[0] if self.text else 0)
                + 2
            )
            pygame.draw.line(
                surf, ACCENT, (cx, self.rect.y + 8), (cx, self.rect.bottom - 8), 2
            )


# ----------------------------------------------------------------------------
# Ring / Rod visual model
# ----------------------------------------------------------------------------


class AnimatedRing:
    """Visual representation of a ring, capable of animating between rods."""

    def __init__(self, ring_id, n_total, color):
        self.id = ring_id
        self.n_total = n_total
        self.color = color
        self.rod = None  # current rod index (1..3), set by caller
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

        # Animation state
        self.animating = False
        self.anim_t = 0.0
        self.anim_duration = 0.5
        self.start_pos = (0, 0)
        self.mid_pos = (0, 0)
        self.end_pos = (0, 0)

    def width_for(self, min_w, max_w):
        if self.n_total <= 1:
            return max_w
        t = (self.id - 1) / (
            self.n_total - 1
        )  # 0 = smallest ring id(1) ... wait ring 1 is smallest
        return lerp(min_w, max_w, t)

    def start_move(self, start_pos, end_pos, arc_height, duration):
        self.animating = True
        self.anim_t = 0.0
        self.anim_duration = duration
        self.start_pos = start_pos
        self.end_pos = end_pos
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = min(start_pos[1], end_pos[1]) - arc_height
        self.mid_pos = (mid_x, mid_y)
        self.x, self.y = start_pos

    def update(self, dt):
        if self.animating:
            self.anim_t += dt / self.anim_duration
            if self.anim_t >= 1.0:
                self.anim_t = 1.0
                self.x, self.y = self.end_pos
                self.animating = False
            else:
                t = ease_in_out_cubic(self.anim_t)
                # Quadratic bezier through start -> mid -> end for a nice arc
                x = (
                    (1 - t) ** 2 * self.start_pos[0]
                    + 2 * (1 - t) * t * self.mid_pos[0]
                    + t**2 * self.end_pos[0]
                )
                y = (
                    (1 - t) ** 2 * self.start_pos[1]
                    + 2 * (1 - t) * t * self.mid_pos[1]
                    + t**2 * self.end_pos[1]
                )
                self.x, self.y = x, y
        else:
            self.x, self.y = self.target_x, self.target_y


class HanoiScene:
    """Manages the visual layout & animation of rods and rings."""

    def __init__(self, area_rect):
        self.area = pygame.Rect(area_rect)
        self.rods_state = {1: [], 2: [], 3: []}  # ring ids bottom->top
        self.rings = {}  # id -> AnimatedRing
        self.n_total = 0
        self.ring_thickness = 26
        self.base_y = 0
        self.rod_x = {1: 0, 2: 0, 3: 0}
        self.rod_top_y = 0
        self.rod_height = 0
        self.min_ring_w = 46
        self.max_ring_w = 0
        self.moving_ring_id = None

    def configure(self, rods_state, n_total):
        self.rods_state = {k: list(v) for k, v in rods_state.items()}
        self.n_total = n_total
        self.rings = {}
        palette_len = len(RING_PALETTE)
        for rod, stack in self.rods_state.items():
            for ring_id in stack:
                color = RING_PALETTE[(ring_id - 1) % palette_len]
                self.rings[ring_id] = AnimatedRing(ring_id, n_total, color)
        self._recompute_geometry()
        self._snap_all_positions()

    def _recompute_geometry(self):
        margin = 60
        usable_w = self.area.width - 2 * margin
        self.rod_x = {
            1: self.area.x + margin + usable_w * 0.17,
            2: self.area.x + margin + usable_w * 0.5,
            3: self.area.x + margin + usable_w * 0.83,
        }
        self.base_y = self.area.bottom - 70
        max_stack = max(self.n_total, 1)
        # Ring thickness shrinks to fit more rings, but the rod itself always
        # fills most of the available vertical space so the scene doesn't look
        # sparse when there are only a few rings.
        self.ring_thickness = clamp(
            int((self.area.height - 170) / max(max_stack, 4)), 14, 32
        )
        available_rod_h = self.area.height - 150
        self.rod_height = clamp(int(available_rod_h), 160, 520)
        self.rod_top_y = self.base_y - self.rod_height
        self.max_ring_w = clamp(int(self.area.width * 0.22), 90, 190)
        self.min_ring_w = clamp(int(self.max_ring_w * 0.34), 34, 70)

    def _slot_pos(self, rod, index):
        """Position (center) of the index-th ring (0 = bottom) on a rod."""
        x = self.rod_x[rod]
        y = self.base_y - self.ring_thickness * index - self.ring_thickness / 2
        return x, y

    def _snap_all_positions(self):
        for rod, stack in self.rods_state.items():
            for i, ring_id in enumerate(stack):
                x, y = self._slot_pos(rod, i)
                ring = self.rings[ring_id]
                ring.x = ring.y = None
                ring.x, ring.y = x, y
                ring.target_x, ring.target_y = x, y

    def resize(self, area_rect):
        self.area = pygame.Rect(area_rect)
        self._recompute_geometry()
        self._snap_all_positions()

    def apply_move(self, ring_id, source, dest, duration=0.5):
        """Kick off animation for moving ring_id from source rod to dest rod."""
        if self.rods_state[source] and self.rods_state[source][-1] == ring_id:
            self.rods_state[source].pop()
        else:
            # defensive: remove wherever it is
            if ring_id in self.rods_state[source]:
                self.rods_state[source].remove(ring_id)
        dest_index = len(self.rods_state[dest])
        self.rods_state[dest].append(ring_id)

        start_pos = (self.rings[ring_id].x, self.rings[ring_id].y)
        end_pos = self._slot_pos(dest, dest_index)
        # A quadratic bezier through (start, mid, end) only reaches the midpoint
        # between the control point and the endpoint average at t=0.5, so to make
        # the curve's actual visual peak clear the rod tops we need to push the
        # control point roughly twice as far past the desired peak height.
        clearance_above_rods = 34
        target_peak_y = self.rod_top_y - clearance_above_rods
        avg_endpoint_y = (start_pos[1] + end_pos[1]) / 2
        control_point_y = 2 * target_peak_y - avg_endpoint_y
        arc_height = min(start_pos[1], end_pos[1]) - control_point_y
        arc_height = max(arc_height, 80)
        self.rings[ring_id].start_move(start_pos, end_pos, arc_height, duration)
        self.rings[ring_id].target_x, self.rings[ring_id].target_y = end_pos
        self.moving_ring_id = ring_id

        # Re-settle any ring that was resting above where this one left from is not needed
        # since stacks are always kept contiguous (top ring moves).

    def instant_set_state(self, rods_state):
        self.rods_state = {k: list(v) for k, v in rods_state.items()}
        self._snap_all_positions()

    def is_animating(self):
        return any(r.animating for r in self.rings.values())

    def update(self, dt):
        for ring in self.rings.values():
            ring.update(dt)
        if (
            self.moving_ring_id is not None
            and not self.rings[self.moving_ring_id].animating
        ):
            self.moving_ring_id = None

    def draw(self, surf, font_small):
        # Base platform (wood)
        base_rect = pygame.Rect(self.area.x + 20, self.base_y, self.area.width - 40, 26)
        shadow_rect = base_rect.copy()
        shadow_rect.y += 10
        rounded_rect(surf, shadow_rect, (0, 0, 0, 0), radius=10)
        pygame.draw.rect(surf, (0, 0, 0), shadow_rect, border_radius=10)
        # (drawn with alpha via separate surface for soft shadow)
        shadow_surf = pygame.Surface(
            (shadow_rect.width, shadow_rect.height + 20), pygame.SRCALPHA
        )
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), shadow_surf.get_rect())
        surf.blit(shadow_surf, (shadow_rect.x, shadow_rect.y - 5))

        rounded_rect(surf, base_rect, WOOD_DARK, radius=10)
        top_strip = pygame.Rect(base_rect.x, base_rect.y, base_rect.width, 8)
        rounded_rect(surf, top_strip, WOOD_LIGHT, radius=6)

        # Rods
        for rod in (1, 2, 3):
            rod_rect = pygame.Rect(
                int(self.rod_x[rod] - 7),
                int(self.rod_top_y),
                14,
                int(self.base_y - self.rod_top_y),
            )
            pygame.draw.rect(surf, ROD_COLOR, rod_rect, border_radius=6)
            highlight_rect = pygame.Rect(rod_rect.x + 2, rod_rect.y, 3, rod_rect.height)
            pygame.draw.rect(surf, ROD_HIGHLIGHT, highlight_rect, border_radius=3)
            # cap
            pygame.draw.circle(
                surf, ROD_HIGHLIGHT, (int(self.rod_x[rod]), int(self.rod_top_y)), 9
            )
            pygame.draw.circle(
                surf, ROD_COLOR, (int(self.rod_x[rod]), int(self.rod_top_y)), 9, 2
            )

            # Rod label
            label = font_small.render(f"Rod {rod}", True, TEXT_DIM)
            surf.blit(
                label, label.get_rect(centerx=self.rod_x[rod], top=self.base_y + 34)
            )

        # Rings: draw non-moving first (bottom to top by rod), then the moving one on top
        moving = self.moving_ring_id
        order = sorted(self.rings.keys())
        for ring_id in order:
            if ring_id == moving:
                continue
            self._draw_ring(surf, self.rings[ring_id], font_small)
        if moving is not None:
            self._draw_ring(surf, self.rings[moving], font_small, is_moving=True)

    def _draw_ring(self, surf, ring, font_small, is_moving=False):
        if ring.x is None:
            return
        w = int(ring.width_for(self.min_ring_w, self.max_ring_w))
        h = self.ring_thickness - 4
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (int(ring.x), int(ring.y))

        if is_moving:
            glow = pygame.Surface((w + 30, h + 30), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*ring.color, 70), glow.get_rect(), border_radius=h)
            surf.blit(glow, glow.get_rect(center=rect.center))

        base_color = ring.color
        top_color = shade(base_color, 1.25)
        bottom_color = shade(base_color, 0.65)

        body_rect = rect
        rounded_rect(surf, body_rect, base_color, radius=h // 2)
        top_band = pygame.Rect(
            body_rect.x, body_rect.y, body_rect.width, max(2, body_rect.height // 3)
        )
        rounded_rect(surf, top_band, top_color, radius=h // 2)
        pygame.draw.rect(surf, (20, 20, 25), body_rect, width=2, border_radius=h // 2)

        # ring number label
        num_str = str(ring.id)
        label_font = font_small
        label = label_font.render(num_str, True, (20, 20, 25))
        surf.blit(label, label.get_rect(center=rect.center))


# ----------------------------------------------------------------------------
# Move log panel
# ----------------------------------------------------------------------------


class MoveLog:
    def __init__(self, rect, font, font_bold, on_move_click=None):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.font_bold = font_bold
        self.entries = []  # list of (move_num, ring, src, dst)
        self.scroll = 0
        self.current_index = 0  # highlighted entry (1-based count of completed moves)
        self.row_h = 26
        self.dragging_scrollbar = False
        self._drag_offset_y = 0
        self.on_move_click = on_move_click

    def _scroll_metrics(self):
        clip = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 42,
            self.rect.width - 16,
            self.rect.height - 52,
        )
        visible_rows = max(1, clip.height // self.row_h)
        total = len(self.entries)
        max_scroll = max(0, total - visible_rows)
        if total <= visible_rows:
            return clip, visible_rows, max_scroll, None
        bar_h = max(20, clip.height * visible_rows / total)
        travel = max(1, clip.height - bar_h)
        bar_y = clip.y + travel * (self.scroll / max_scroll if max_scroll else 0)
        bar_rect = pygame.Rect(self.rect.right - 12, int(bar_y), 8, int(bar_h))
        return clip, visible_rows, max_scroll, bar_rect

    def set_entries(self, seq):
        self.entries = []
        for m in sorted(seq.keys()):
            ring, src, dst = seq[m]
            self.entries.append((m, ring, src, dst))
        self.scroll = 0
        self.current_index = 0

    def ensure_visible(self, index):
        visible_rows = (self.rect.height - 50) // self.row_h
        if index < self.scroll:
            self.scroll = index
        elif index >= self.scroll + visible_rows:
            self.scroll = index - visible_rows + 1
        self.scroll = max(0, self.scroll)

    def handle_event(self, event):
        mouse_pos = event.pos if hasattr(event, "pos") else pygame.mouse.get_pos()
        clip, _, max_scroll, bar_rect = self._scroll_metrics()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if bar_rect and bar_rect.inflate(8, 4).collidepoint(mouse_pos):
                self.dragging_scrollbar = True
                self._drag_offset_y = mouse_pos[1] - bar_rect.y
                return True

            # Clicking a move row jumps the visualizer directly to that move.
            if clip.collidepoint(mouse_pos):
                row_index = self.scroll + (mouse_pos[1] - clip.y) // self.row_h
                row_y = clip.y + (row_index - self.scroll) * self.row_h
                row_rect = pygame.Rect(clip.x, row_y, clip.width, self.row_h - 2)
                if (
                    0 <= row_index < len(self.entries)
                    and row_rect.collidepoint(mouse_pos)
                ):
                    move_num = self.entries[row_index][0]
                    if self.on_move_click:
                        self.on_move_click(move_num)
                    return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_scrollbar = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_scrollbar and bar_rect:
            current_bar_h = bar_rect.height
            travel = max(1, clip.height - current_bar_h)
            new_bar_y = clamp(
                mouse_pos[1] - self._drag_offset_y,
                clip.y,
                clip.bottom - current_bar_h,
            )
            ratio = (new_bar_y - clip.y) / travel
            self.scroll = int(round(ratio * max_scroll))
            return True
        elif event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(mouse_pos):
            self.scroll -= event.y * 2
            self.scroll = clamp(self.scroll, 0, max_scroll)
            return True
        return False

    def draw(self, surf):
        rounded_rect(
            surf,
            self.rect,
            PANEL_BG,
            radius=14,
            border_color=PANEL_BORDER,
            border_width=2,
        )
        header = self.font_bold.render("Move Log", True, TEXT_MAIN)
        surf.blit(header, (self.rect.x + 16, self.rect.y + 12))
        count_text = self.font.render(
            f"{self.current_index}/{len(self.entries)}", True, TEXT_DIM
        )
        surf.blit(
            count_text,
            count_text.get_rect(right=self.rect.right - 16, top=self.rect.y + 14),
        )

        clip = pygame.Rect(
            self.rect.x + 8,
            self.rect.y + 42,
            self.rect.width - 16,
            self.rect.height - 52,
        )
        old_clip = surf.get_clip()
        surf.set_clip(clip)

        y = clip.y - (self.scroll * self.row_h) + (self.scroll * 0)
        visible_start = self.scroll
        for i in range(visible_start, len(self.entries)):
            m, ring, src, dst = self.entries[i]
            row_y = clip.y + (i - visible_start) * self.row_h
            if row_y > clip.bottom:
                break
            done = (i + 1) <= self.current_index
            is_next = (i + 1) == self.current_index + 1
            row_rect = pygame.Rect(clip.x, row_y, clip.width, self.row_h - 2)
            if is_next:
                rounded_rect(surf, row_rect, ACCENT_DIM, radius=6)
            color = TEXT_MAIN if done else (TEXT_DIM if not is_next else TEXT_MAIN)
            txt = f"{m:>3}.  ring {ring}:  rod {src} -> rod {dst}"
            txt_surf = self.font.render(
                txt, True, color if not done else shade(SUCCESS, 1.0)
            )
            surf.blit(txt_surf, (row_rect.x + 8, row_rect.y + 4))

        surf.set_clip(old_clip)

        # draggable scrollbar
        _, _, _, bar_rect = self._scroll_metrics()
        if bar_rect:
            track_rect = pygame.Rect(self.rect.right - 12, clip.y, 8, clip.height)
            rounded_rect(surf, track_rect, PANEL_BG_LIGHT, radius=4)
            rounded_rect(
                surf,
                bar_rect,
                shade(ACCENT, 1.0) if self.dragging_scrollbar else ACCENT_DIM,
                radius=4,
            )


# ----------------------------------------------------------------------------
# Application (state machine)
# ----------------------------------------------------------------------------

STATE_MAIN_MENU = "main_menu"
STATE_CLASSIC_SETUP = "classic_setup"
STATE_CUSTOM_SETUP = "custom_setup"
STATE_PRESET_SETUP = "preset_setup"
STATE_VISUALIZER = "visualizer"
STATE_PLAY_SETUP = "play_setup"
STATE_PLAY = "play"
STATE_MESSAGE = "message"  # transient error overlay
SAVE_DIALOG_W = 660
SAVE_DIALOG_H = 250


class HanoiApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tower of Hanoi — Visual Solver")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.font_title = pygame.font.Font(FONT_NAME, 50)
        self.font_h2 = pygame.font.Font(FONT_NAME, 32)
        self.font_body = pygame.font.Font(FONT_NAME, 28)
        self.font_body_bold = pygame.font.Font(FONT_NAME, 28)
        self.font_body_bold.set_bold(True)
        self.font_small = pygame.font.Font(FONT_NAME, 24)
        self.font_mono = pygame.font.Font(FONT_NAME, 26)
        self.font_ring = pygame.font.Font(FONT_NAME, 24)
        self.font_ring.set_bold(True)

        self.state = STATE_MAIN_MENU
        self.buttons = []
        self.text_inputs = []

        self.error_message = None
        self.info_message = None
        self.message_timer = 0.0

        # Solve/visualizer state
        self.rods = None
        self.target = None
        self.seq = None
        self.n_total = 0
        self.scene = HanoiScene((0, 0, 100, 100))
        self.move_log = MoveLog(
            (0, 0, 100, 100),
            self.font_mono,
            self.font_body_bold,
            on_move_click=self._jump_to_move,
        )
        self.move_index = 0  # number of moves completed
        self.auto_play = False
        self.auto_timer = 0.0
        self.speed_options = [4.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02]
        self.speed_labels = ["0.25x", "0.5x", "1x", "2x", "5x", "10x", "20x", "50x"]
        self.speed_index = 2
        self.move_duration = self.speed_options[self.speed_index]
        self.solved_complete = False
        self.save_feedback = None
        self.save_feedback_timer = 0.0
        self.verify_feedback = None
        self.verify_feedback_timer = 0.0

        # Classic setup fields
        self.classic_n_input = TextInput(
            (0, 0, 10, 10),
            self.font_body,
            placeholder="e.g. 4",
            numeric=True,
            initial="4",
        )
        self.classic_start_rod = 1
        self.classic_target_rod = 3

        # Custom setup fields
        self.custom_inputs = {
            1: TextInput((0, 0, 10, 10), self.font_body, placeholder="e.g. 3, 2, 1"),
            2: TextInput((0, 0, 10, 10), self.font_body, placeholder="empty"),
            3: TextInput((0, 0, 10, 10), self.font_body, placeholder="empty"),
        }
        self.custom_target_rod = 1

        # Presets
        self.problems = self._load_problems()
        self.preset_scroll = 0
        self.preset_selected = None
        self.preset_dragging_scrollbar = False
        self._preset_drag_offset_y = 0

        # Save-as-preset dialog
        self.save_dialog_open = False
        self.save_description_input = TextInput(
            (0, 0, 10, 10),
            self.font_body,
            placeholder="Describe this problem",
        )

        # Play mode setup fields (reuses the same per-rod text-input idea as
        # Custom Mode, plus a target rod that defines the "solved" state).
        self.play_setup_inputs = {
            1: TextInput((0, 0, 10, 10), self.font_body, placeholder="e.g. 3, 2, 1"),
            2: TextInput((0, 0, 10, 10), self.font_body, placeholder="empty"),
            3: TextInput((0, 0, 10, 10), self.font_body, placeholder="empty"),
        }
        self.play_target_rod = 3

        # Play mode board state
        self.play_scene = HanoiScene((0, 0, 100, 100))
        self.play_rods = None
        self.play_rods_initial = None
        self.play_target = None
        self.play_n_total = 0
        self.play_optimal_moves = 0
        self.play_move_count = 0
        self.play_elapsed = 0.0
        self.play_running = False   # timer running (paused once solved)
        self.play_solved = False
        self.play_selected_rod = None      # click-to-select source rod
        self.play_drag_ring_id = None      # ring id currently being dragged
        self.play_drag_source_rod = None
        self.play_drag_pos = (0, 0)
        self.play_drag_offset = (0, 0)
        self.play_invalid_flash_rod = None
        self.play_invalid_flash_timer = 0.0
        self.play_win_toast_shown = False

        self.layout_dirty = True
        self.build_main_menu()

    # ---------------------------- data ----------------------------

    def _load_problems(self):
        problems = {}
        try:
            with open("problems.json", "r") as f:
                data = json.load(f)
            problems.update(data.get("problems", {}))
        except Exception:
            pass
        return problems

    def _persist_saved_problem(self, description):
        # Save every new problem directly in problems.json, using the next numeric index.
        path = os.path.abspath("problems.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"problems": {}}

        problems = data.setdefault("problems", {})

        # Existing presets use numeric string keys ("1", "2", ...). Also tolerate
        # integer keys or legacy "saved_N" keys when determining the next index.
        numeric_ids = []
        for key in problems:
            try:
                numeric_ids.append(int(key))
                continue
            except (TypeError, ValueError):
                pass
            if isinstance(key, str) and key.startswith("saved_"):
                try:
                    numeric_ids.append(int(key.split("_", 1)[1]))
                except ValueError:
                    pass

        next_id = max(numeric_ids, default=0) + 1
        key = str(next_id)
        problem = {
            "initial_state": {str(k): list(v) for k, v in self.rods.items()},
            "target": self.target,
            "description": description,
        }
        problems[key] = problem

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        self.problems[key] = problem
        return key

    def _preset_scroll_metrics(self):
        rect = self.preset_list_rect
        row_h = 74
        total_h = row_h * len(self.problems)
        if total_h <= rect.height:
            return 0, None
        bar_h = max(30, rect.height * rect.height / total_h)
        max_scroll = max(1, total_h - rect.height)
        travel = max(1, rect.height - bar_h)
        bar_y = rect.y + travel * (self.preset_scroll / max_scroll)
        bar_rect = pygame.Rect(rect.right - 14, int(bar_y), 10, int(bar_h))
        return max_scroll, bar_rect

    # ---------------------------- helpers ----------------------------

    def show_error(self, msg):
        self.error_message = msg
        self.message_timer = 3.2

    def show_info(self, msg):
        self.info_message = msg
        self.message_timer = 2.2

    def set_state(self, state):
        self.state = state
        if state == STATE_MAIN_MENU:
            self.build_main_menu()
        elif state == STATE_CLASSIC_SETUP:
            self.build_classic_setup()
        elif state == STATE_CUSTOM_SETUP:
            self.build_custom_setup()
        elif state == STATE_PRESET_SETUP:
            self.build_preset_setup()
        elif state == STATE_PLAY_SETUP:
            self.build_play_setup()
        elif state == STATE_PLAY:
            self.build_play_layout()

    # ---------------------------- layout builders ----------------------------

    def build_main_menu(self):
        self.buttons = []
        cx = self.screen.get_width() // 2
        sh = self.screen.get_height()
        w, h, gap = 420, 76, 22
        labels = [
            (
                "Classic Mode",
                "All rings on one rod, move to target",
                lambda: self.set_state(STATE_CLASSIC_SETUP),
            ),
            (
                "Custom Mode",
                "Place rings on rods yourself",
                lambda: self.set_state(STATE_CUSTOM_SETUP),
            ),
            (
                "Play Mode",
                "Set up a puzzle and solve it by hand",
                lambda: self.set_state(STATE_PLAY_SETUP),
            ),
            (
                "Preset Problems",
                "Choose from built-in and saved puzzles",
                lambda: self.set_state(STATE_PRESET_SETUP),
            ),
            ("Quit", None, self.quit),
        ]
        total_h = len(labels) * h + (len(labels) - 1) * gap
        # Reserve room below the menu for the decorative towers + a margin above the bottom.
        deco_reserve = 150
        available_top = 130
        available_bottom = sh - deco_reserve
        y = available_top + max(0, (available_bottom - available_top - total_h) // 2)
        self.menu_bottom_y = y
        for i, (label, subtitle, cb) in enumerate(labels):
            style = (
                "primary" if i == 0 else ("danger" if label == "Quit" else "secondary")
            )
            btn = Button(
                (cx - w // 2, y, w, h),
                label,
                self.font_h2,
                on_click=cb,
                style=style,
                subtitle=subtitle,
            )
            self.buttons.append(btn)
            y += h + gap
        self.menu_bottom_y = y - gap

    def build_classic_setup(self):
        self.buttons = []
        cx = self.screen.get_width() // 2
        panel_w = 560
        left = cx - panel_w // 2
        y = 250

        self.classic_n_input.rect = pygame.Rect(left + 220, y, 140, 44)

        # start rod buttons
        rod_y = y + 90
        self.classic_start_buttons = []
        for i, rod in enumerate((1, 2, 3)):
            bx = left + 220 + i * 90
            btn = Button(
                (bx, rod_y, 76, 44),
                str(rod),
                self.font_body_bold,
                on_click=(lambda r=rod: self._set_classic_start(r)),
                style=("primary" if rod == self.classic_start_rod else "secondary"),
            )
            self.classic_start_buttons.append(btn)

        target_y = rod_y + 90
        self.classic_target_buttons = []
        for i, rod in enumerate((1, 2, 3)):
            bx = left + 220 + i * 90
            enabled = rod != self.classic_start_rod
            btn = Button(
                (bx, target_y, 76, 44),
                str(rod),
                self.font_body_bold,
                on_click=(lambda r=rod: self._set_classic_target(r)),
                style=("primary" if rod == self.classic_target_rod else "secondary"),
                enabled=enabled,
            )
            self.classic_target_buttons.append(btn)

        action_y = target_y + 100
        self.buttons.append(
            Button(
                (left, action_y, 170, 52),
                "Back",
                self.font_body_bold,
                on_click=lambda: self.set_state(STATE_MAIN_MENU),
                style="secondary",
            )
        )
        self.buttons.append(
            Button(
                (left + panel_w - 220, action_y, 220, 52),
                "Solve & Visualize",
                self.font_body_bold,
                on_click=self._submit_classic,
                style="primary",
            )
        )

    def _set_classic_start(self, rod):
        self.classic_start_rod = rod
        if self.classic_target_rod == rod:
            self.classic_target_rod = next(r for r in (1, 2, 3) if r != rod)
        self.build_classic_setup()

    def _set_classic_target(self, rod):
        if rod == self.classic_start_rod:
            return
        self.classic_target_rod = rod
        self.build_classic_setup()

    def build_custom_setup(self):
        self.buttons = []
        cx = self.screen.get_width() // 2
        panel_w = 640
        left = cx - panel_w // 2
        y = 210
        row_h = 64
        for i, rod in enumerate((1, 2, 3)):
            self.custom_inputs[rod].rect = pygame.Rect(
                left + 170, y + i * row_h, panel_w - 170, 44
            )

        target_y = y + 3 * row_h + 20
        self.custom_target_buttons = []
        for i, rod in enumerate((1, 2, 3)):
            bx = left + 170 + i * 90
            btn = Button(
                (bx, target_y, 76, 44),
                str(rod),
                self.font_body_bold,
                on_click=(lambda r=rod: self._set_custom_target(r)),
                style=("primary" if rod == self.custom_target_rod else "secondary"),
            )
            self.custom_target_buttons.append(btn)

        action_y = target_y + 90
        self.buttons.append(
            Button(
                (left, action_y, 170, 52),
                "Back",
                self.font_body_bold,
                on_click=lambda: self.set_state(STATE_MAIN_MENU),
                style="secondary",
            )
        )
        self.buttons.append(
            Button(
                (left + panel_w - 220, action_y, 220, 52),
                "Solve & Visualize",
                self.font_body_bold,
                on_click=self._submit_custom,
                style="primary",
            )
        )

    def _set_custom_target(self, rod):
        self.custom_target_rod = rod
        self.build_custom_setup()

    def build_play_setup(self):
        self.buttons = []
        cx = self.screen.get_width() // 2
        panel_w = 640
        left = cx - panel_w // 2
        y = 210
        row_h = 64
        for i, rod in enumerate((1, 2, 3)):
            self.play_setup_inputs[rod].rect = pygame.Rect(
                left + 170, y + i * row_h, panel_w - 170, 44
            )

        target_y = y + 3 * row_h + 20
        self.play_target_buttons = []
        for i, rod in enumerate((1, 2, 3)):
            bx = left + 170 + i * 90
            btn = Button(
                (bx, target_y, 76, 44),
                str(rod),
                self.font_body_bold,
                on_click=(lambda r=rod: self._set_play_target(r)),
                style=("primary" if rod == self.play_target_rod else "secondary"),
            )
            self.play_target_buttons.append(btn)

        action_y = target_y + 90
        self.buttons.append(
            Button(
                (left, action_y, 170, 52),
                "Back",
                self.font_body_bold,
                on_click=lambda: self.set_state(STATE_MAIN_MENU),
                style="secondary",
            )
        )
        self.buttons.append(
            Button(
                (left + panel_w - 220, action_y, 220, 52),
                "Start Playing",
                self.font_body_bold,
                on_click=self._submit_play_setup,
                style="primary",
            )
        )

    def _set_play_target(self, rod):
        self.play_target_rod = rod
        self.build_play_setup()

    def build_preset_setup(self):
        self.buttons = []
        left = 60
        top = 170
        list_w = self.screen.get_width() - 120
        list_h = self.screen.get_height() - 320
        self.preset_list_rect = pygame.Rect(left, top, list_w, list_h)

        action_y = top + list_h + 24
        self.buttons.append(
            Button(
                (left, action_y, 170, 52),
                "Back",
                self.font_body_bold,
                on_click=lambda: self.set_state(STATE_MAIN_MENU),
                style="secondary",
            )
        )
        solve_btn = Button(
            (left + list_w - 220, action_y, 220, 52),
            "Solve & Visualize",
            self.font_body_bold,
            on_click=self._submit_preset,
            style="primary",
            enabled=self.preset_selected is not None,
        )
        self.buttons.append(solve_btn)

    def build_visualizer_layout(self):
        self.buttons = []
        w, h = self.screen.get_width(), self.screen.get_height()

        # Log panel narrows on smaller windows so the scene keeps breathing room.
        log_w = clamp(int(w * 0.27), 220, 340)

        # Decide between a one-row (wide window) or two-row (narrow window)
        # control bar based on how much horizontal space we actually have.
        one_row_min_width = 1080
        two_row = w < one_row_min_width
        bar_row_h = 52
        bar_gap = 10
        bar_rows = 2 if two_row else 1
        bar_total_h = bar_rows * bar_row_h + (bar_rows - 1) * bar_gap

        bar_top_y = h - 20 - bar_total_h
        scene_area = (20, 80, w - log_w - 40, bar_top_y - 100)
        self.scene.resize(scene_area)
        self.move_log.rect = pygame.Rect(w - log_w - 10, 80, log_w, bar_top_y - 100)

        row1_y = bar_top_y
        row2_y = bar_top_y + bar_row_h + bar_gap if two_row else bar_top_y

        # --- Row 1: transport controls ---
        bx = 20
        self.buttons.append(
            Button(
                (bx, row1_y, 100, bar_row_h),
                "Back",
                self.font_body_bold,
                on_click=self._back_from_visualizer,
                style="secondary",
            )
        )
        bx += 112
        self.btn_step_back = Button(
            (bx, row1_y, 46, bar_row_h),
            "<",
            self.font_h2,
            on_click=self._step_back,
            style="secondary",
        )
        self.buttons.append(self.btn_step_back)
        bx += 54
        self.btn_play = Button(
            (bx, row1_y, 100, bar_row_h),
            "Play",
            self.font_body_bold,
            on_click=self._toggle_play,
            style="primary",
        )
        self.buttons.append(self.btn_play)
        bx += 112
        self.btn_step_fwd = Button(
            (bx, row1_y, 46, bar_row_h),
            ">",
            self.font_h2,
            on_click=self._step_fwd,
            style="secondary",
        )
        self.buttons.append(self.btn_step_fwd)
        bx += 58
        self.buttons.append(
            Button(
                (bx, row1_y, 92, bar_row_h),
                "Reset",
                self.font_body_bold,
                on_click=self._reset_playback,
                style="secondary",
            )
        )
        bx += 104
        self.buttons.append(
            Button(
                (bx, row1_y, 110, bar_row_h),
                "Skip End",
                self.font_body_bold,
                on_click=self._skip_to_end,
                style="secondary",
            )
        )
        bx += 122

        if not two_row:
            self._layout_speed_and_save(bx, row1_y, w, bar_row_h)
        else:
            # --- Row 2: speed + save/verify, right-aligned ---
            self._layout_speed_and_save(20, row2_y, w, bar_row_h)

        self.control_bar_top_y = row1_y

    def _layout_speed_and_save(self, bx, y, w, bar_row_h):
        self.speed_minus_btn = Button(
            (bx, y, 38, bar_row_h),
            "-",
            self.font_h2,
            on_click=self._speed_down,
            style="secondary",
        )
        self.buttons.append(self.speed_minus_btn)
        bx += 44
        self.speed_label_center_x = bx + 34
        self.speed_label_center_y = y + bar_row_h // 2
        bx += 68
        self.speed_plus_btn = Button(
            (bx, y, 38, bar_row_h),
            "+",
            self.font_h2,
            on_click=self._speed_up,
            style="secondary",
        )
        self.buttons.append(self.speed_plus_btn)

        # Save / Verify pinned to the right edge of the window.
        right_x = w - 20 - 150
        self.buttons.append(
            Button(
                (right_x, y, 150, bar_row_h),
                "Verify Solution",
                self.font_body_bold,
                on_click=self._verify_current,
                style="secondary",
            )
        )
        self.buttons.append(
            Button(
                (right_x - 164, y, 150, bar_row_h),
                "Save Solution",
                self.font_body_bold,
                on_click=self._save_current,
                style="secondary",
            )
        )

    def build_play_layout(self):
        self.buttons = []
        w, h = self.screen.get_width(), self.screen.get_height()
        bar_row_h = 52
        bar_top_y = h - 20 - bar_row_h
        scene_area = (20, 110, w - 40, bar_top_y - 130)
        self.play_scene.resize(scene_area)

        bx = 20
        self.buttons.append(
            Button(
                (bx, bar_top_y, 100, bar_row_h),
                "Back",
                self.font_body_bold,
                on_click=self._back_from_play,
                style="secondary",
            )
        )
        bx += 112
        self.buttons.append(
            Button(
                (bx, bar_top_y, 120, bar_row_h),
                "Restart",
                self.font_body_bold,
                on_click=self._restart_play,
                style="secondary",
            )
        )
        self.play_control_bar_top_y = bar_top_y

    # ---------------------------- submit handlers ----------------------------

    def _submit_classic(self):
        n_text = self.classic_n_input.text.strip()
        try:
            n = int(n_text)
        except ValueError:
            self.show_error("Please enter a valid integer for number of rings.")
            return
        if n < 1:
            self.show_error("The number of rings must be at least 1.")
            return
        if n > 16:
            self.show_error(
                "Please choose 16 rings or fewer for a clear visualization."
            )
            return
        start = self.classic_start_rod
        target = self.classic_target_rod
        if start == target:
            self.show_error("Starting and target rods must be different.")
            return
        rods = {1: [], 2: [], 3: []}
        rods[start] = list(range(n, 0, -1))
        if not is_valid_rods_state(rods):
            self.show_error("Invalid configuration.")
            return
        self._start_solution(rods, target)

    def _parse_rod_inputs(self, inputs, max_rings=16):
        """Parse the three per-rod text inputs into a rods dict, or return
        (None, error_message) if invalid. Shared by Custom Mode and Play Mode
        setup screens, which use the same comma-separated-per-rod format."""
        rods = {1: [], 2: [], 3: []}
        try:
            for rod in (1, 2, 3):
                text = inputs[rod].text.strip()
                if not text:
                    rods[rod] = []
                    continue
                rings = [int(x.strip()) for x in text.split(",") if x.strip() != ""]
                rods[rod] = rings
        except ValueError:
            return None, "Please enter valid integers separated by commas."
        total = len(rods[1]) + len(rods[2]) + len(rods[3])
        if total == 0:
            return None, "At least one ring must be placed on a rod."
        if total > max_rings:
            return None, f"Please use {max_rings} rings or fewer for a clear visualization."
        if not is_valid_rods_state(rods):
            return None, "Invalid configuration — check ring order and numbering."
        return rods, None

    def _submit_custom(self):
        rods, error = self._parse_rod_inputs(self.custom_inputs)
        if error:
            self.show_error(error)
            return
        self._start_solution(rods, self.custom_target_rod)

    def _submit_play_setup(self):
        rods, error = self._parse_rod_inputs(self.play_setup_inputs)
        if error:
            self.show_error(error)
            return
        total = sum(len(v) for v in rods.values())
        already_solved = len(rods[self.play_target_rod]) == total
        if already_solved:
            self.show_error("This puzzle is already solved — rings are already on the target rod.")
            return
        self.play_rods_initial = {k: list(v) for k, v in rods.items()}
        self._start_play(rods, self.play_target_rod)

    def _submit_preset(self):
        if self.preset_selected is None:
            self.show_error("Select a problem first.")
            return
        problem = self.problems[self.preset_selected]
        rods = {
            1: list(problem["initial_state"]["1"]),
            2: list(problem["initial_state"]["2"]),
            3: list(problem["initial_state"]["3"]),
        }
        target = problem["target"]
        if not is_valid_rods_state(rods):
            self.show_error(
                f"Problem {self.preset_selected} has an invalid configuration."
            )
            return
        self._start_solution(rods, target)

    def _start_solution(self, rods, target):
        try:
            seq = compute_full_sequence(rods, target)
        except Exception as e:
            self.show_error(f"Failed to compute solution: {e}")
            return
        self.rods = rods
        self.target = target
        self.seq = seq
        self.n_total = len(rods[1]) + len(rods[2]) + len(rods[3])
        self.scene.configure(rods, self.n_total)
        self.move_log.set_entries(seq)
        self.move_index = 0
        self.auto_play = False
        self.solved_complete = len(seq) == 0
        self.save_feedback = None
        self.verify_feedback = None
        self.set_state(STATE_VISUALIZER)
        self.build_visualizer_layout()

    def _start_play(self, rods, target):
        """Initialize Play Mode: the user must solve the puzzle by hand."""
        # We compute the optimal move count up front (for the end-of-game
        # comparison) but deliberately never show the move sequence itself.
        try:
            optimal_seq = compute_full_sequence(rods, target)
        except Exception as e:
            self.show_error(f"Failed to prepare puzzle: {e}")
            return
        self.play_rods = {k: list(v) for k, v in rods.items()}
        self.play_target = target
        self.play_n_total = sum(len(v) for v in rods.values())
        self.play_optimal_moves = len(optimal_seq)
        self.play_scene.configure(self.play_rods, self.play_n_total)
        self.play_move_count = 0
        self.play_elapsed = 0.0
        self.play_running = True
        self.play_solved = False
        self.play_selected_rod = None
        self.play_drag_ring_id = None
        self.play_drag_source_rod = None
        self.play_invalid_flash_rod = None
        self.play_invalid_flash_timer = 0.0
        self.play_win_toast_shown = False
        self.set_state(STATE_PLAY)
        self.build_play_layout()

    # ---------------------------- visualizer controls ----------------------------

    def _back_from_visualizer(self):
        self.auto_play = False
        self.set_state(STATE_MAIN_MENU)

    def _can_step_fwd(self):
        return (
            self.seq is not None
            and self.move_index < len(self.seq)
            and not self.scene.is_animating()
        )

    def _can_step_back(self):
        return (
            self.seq is not None
            and self.move_index > 0
            and not self.scene.is_animating()
        )

    def _step_fwd(self):
        if not self._can_step_fwd():
            return
        self.move_index += 1
        ring, src, dst = self.seq[self.move_index]
        self.scene.apply_move(ring, src, dst, duration=self.move_duration)
        self.move_log.current_index = self.move_index
        self.move_log.ensure_visible(self.move_index)
        if self.move_index >= len(self.seq):
            self.solved_complete = True
            self.auto_play = False

    def _step_back(self):
        if not self._can_step_back():
            return
        # Rebuild state up to move_index - 1 (simplest robust approach: replay from scratch)
        self.move_index -= 1
        self._rebuild_to_index(self.move_index, animate_last=True)

    def _jump_to_move(self, move_num):
        if self.seq is None or self.scene.is_animating():
            return
        if move_num < 0 or move_num > len(self.seq):
            return

        self.auto_play = False
        self.move_index = move_num
        self._rebuild_to_index(move_num)

    def _rebuild_to_index(self, index, animate_last=False):
        # Reconstruct rods_state up to `index` moves applied, then snap scene instantly,
        # optionally animating the very last step for a nice "undo" feel.
        current = {k: list(v) for k, v in self.rods.items()}
        for m in range(1, index + 1):
            ring, src, dst = self.seq[m]
            if current[src] and current[src][-1] == ring:
                current[src].pop()
            current[dst].append(ring)
        self.scene.instant_set_state(current)
        self.move_log.current_index = index
        self.move_log.ensure_visible(index)
        self.solved_complete = index >= len(self.seq)

    def _reset_playback(self):
        self.auto_play = False
        self.move_index = 0
        self.scene.instant_set_state(self.rods)
        self.move_log.current_index = 0
        self.move_log.scroll = 0
        self.solved_complete = len(self.seq) == 0

    def _skip_to_end(self):
        self.auto_play = False
        self.move_index = len(self.seq)
        self._rebuild_to_index(self.move_index)

    def _toggle_play(self):
        if self.move_index >= len(self.seq):
            self._reset_playback()
        self.auto_play = not self.auto_play
        self.auto_timer = 0.0

    def _speed_down(self):
        self.speed_index = clamp(self.speed_index - 1, 0, len(self.speed_options) - 1)
        self.move_duration = self.speed_options[self.speed_index]

    def _speed_up(self):
        self.speed_index = clamp(self.speed_index + 1, 0, len(self.speed_options) - 1)
        self.move_duration = self.speed_options[self.speed_index]

    def _save_current(self):
        if self.rods is None or self.seq is None:
            return
        self.save_dialog_open = True
        self.save_description_input.text = ""
        self.save_description_input.active = True
        self.save_description_input.cursor_visible = True
        self.save_dialog_error = None

    def _confirm_save_problem(self):
        if self.rods is None or self.seq is None:
            return
        description = self.save_description_input.text.strip()
        if not description:
            self.save_dialog_error = "Please enter a description."
            self.save_description_input.active = True
            return
        try:
            self._persist_saved_problem(description)
            ok = save_solution(self.rods, self.target, self.seq, "solutions.json")
        except Exception:
            ok = False
        self.save_dialog_open = False
        self.save_description_input.active = False
        self.save_feedback = "Saved as preset!" if ok else "Saved preset; solution save failed."
        self.save_feedback_timer = 2.5

    def _cancel_save_problem(self):
        self.save_dialog_open = False
        self.save_description_input.active = False
        self.save_dialog_error = None

    def _verify_current(self):
        if self.rods is None or self.seq is None:
            return
        # verify_solution prints to stdout; capture result only
        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = verify_solution(self.rods, self.seq, self.target)
        self.verify_feedback = "Valid solution!" if ok else "Invalid solution."
        self.verify_feedback_timer = 2.5

    # ---------------------------- play mode controls ----------------------------

    def _back_from_play(self):
        self.set_state(STATE_MAIN_MENU)

    def _restart_play(self):
        if self.play_target is None:
            return
        self._start_play(self.play_rods_initial, self.play_target)

    def _play_can_move(self, source_rod, dest_rod):
        """A move is legal iff the source rod has a ring and the destination
        rod is empty or its top ring is larger (numerically greater id, by
        this project's convention that ring 1 is smallest)."""
        if source_rod == dest_rod:
            return False
        stack = self.play_scene.rods_state.get(source_rod)
        if not stack:
            return False
        moving_ring = stack[-1]
        dest_stack = self.play_scene.rods_state.get(dest_rod)
        if dest_stack:
            return moving_ring < dest_stack[-1]
        return True

    def _play_flash_invalid(self, rod):
        self.play_invalid_flash_rod = rod
        self.play_invalid_flash_timer = 0.35

    def _play_attempt_move(self, source_rod, dest_rod):
        """Try to move the top ring of source_rod onto dest_rod. Returns True
        if the move was made."""
        if not self._play_can_move(source_rod, dest_rod):
            self._play_flash_invalid(dest_rod)
            return False
        ring_id = self.play_scene.rods_state[source_rod][-1]
        self.play_scene.apply_move(ring_id, source_rod, dest_rod, duration=0.28)
        self.play_move_count += 1
        self._play_check_win()
        return True

    def _play_check_win(self):
        target_stack = self.play_scene.rods_state.get(self.play_target, [])
        if len(target_stack) == self.play_n_total:
            self.play_solved = True
            self.play_running = False

    def _play_rod_at_pos(self, pos):
        """Which rod (1/2/3) a screen position is closest to, if it's within
        a reasonably generous horizontal band of that rod, else None."""
        scene = self.play_scene
        best_rod, best_dist = None, None
        band = max(70, (scene.max_ring_w // 2) + 20)
        for rod, x in scene.rod_x.items():
            dist = abs(pos[0] - x)
            if dist <= band and (best_dist is None or dist < best_dist):
                best_rod, best_dist = rod, dist
        return best_rod

    def _play_topmost_ring_hit(self, pos):
        """If pos is over the topmost ring of some rod, return that rod,
        else None. Used to start a drag."""
        scene = self.play_scene
        for rod, stack in scene.rods_state.items():
            if not stack:
                continue
            ring_id = stack[-1]
            ring = scene.rings.get(ring_id)
            if ring is None or ring.animating:
                continue
            w = int(ring.width_for(scene.min_ring_w, scene.max_ring_w))
            hgt = scene.ring_thickness
            rect = pygame.Rect(0, 0, w, hgt)
            rect.center = (int(ring.x), int(ring.y))
            if rect.collidepoint(pos):
                return rod
        return None

    def _play_handle_event(self, event):
        """Returns True if the event was consumed by play-mode board logic."""
        if self.play_scene.is_animating():
            # Don't allow starting new interactions mid-animation, but do let
            # button clicks (Back/Restart) through untouched.
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.play_scene.area.collidepoint(event.pos) and \
                    event.pos[1] > self.play_scene.area.bottom:
                return False
            rod_hit = self._play_topmost_ring_hit(event.pos)
            if rod_hit is not None:
                # Start a drag of the topmost ring on that rod.
                ring_id = self.play_scene.rods_state[rod_hit][-1]
                ring = self.play_scene.rings[ring_id]
                self.play_drag_ring_id = ring_id
                self.play_drag_source_rod = rod_hit
                self.play_drag_offset = (event.pos[0] - ring.x, event.pos[1] - ring.y)
                self.play_drag_pos = (ring.x, ring.y)
                self.play_scene.moving_ring_id = ring_id
                self.play_selected_rod = None
                return True
            # Not on a ring: treat as a click-to-select on the nearest rod.
            rod_near = self._play_rod_at_pos(event.pos)
            if rod_near is not None:
                if self.play_selected_rod is None:
                    if self.play_scene.rods_state.get(rod_near):
                        self.play_selected_rod = rod_near
                    else:
                        self._play_flash_invalid(rod_near)
                elif self.play_selected_rod == rod_near:
                    self.play_selected_rod = None
                else:
                    self._play_attempt_move(self.play_selected_rod, rod_near)
                    self.play_selected_rod = None
                return True
            return False

        elif event.type == pygame.MOUSEMOTION:
            if self.play_drag_ring_id is not None:
                self.play_drag_pos = (
                    event.pos[0] - self.play_drag_offset[0],
                    event.pos[1] - self.play_drag_offset[1],
                )
                ring = self.play_scene.rings[self.play_drag_ring_id]
                ring.x, ring.y = self.play_drag_pos
                return True
            return False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.play_drag_ring_id is not None:
                dest_rod = self._play_rod_at_pos(event.pos)
                source_rod = self.play_drag_source_rod
                ring_id = self.play_drag_ring_id
                self.play_drag_ring_id = None
                self.play_drag_source_rod = None
                self.play_scene.moving_ring_id = None
                if dest_rod is None or not self._play_attempt_move(source_rod, dest_rod):
                    # Snap back to its resting slot on the source rod.
                    idx = len(self.play_scene.rods_state[source_rod]) - 1
                    x, y = self.play_scene._slot_pos(source_rod, max(idx, 0))
                    ring = self.play_scene.rings[ring_id]
                    ring.x, ring.y = x, y
                    ring.target_x, ring.target_y = x, y
                return True
            return False

        return False

    # ---------------------------- event loop ----------------------------

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            elif event.type == pygame.VIDEORESIZE:
                new_w = max(event.w, MIN_SCREEN_W)
                new_h = max(event.h, MIN_SCREEN_H)
                self.screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                self.set_state(self.state)
                if self.state == STATE_VISUALIZER:
                    self.build_visualizer_layout()
                elif self.state == STATE_PLAY:
                    self.build_play_layout()
                continue

            # Save-description modal captures input before the underlying visualizer controls.
            if self.state == STATE_VISUALIZER and self.save_dialog_open:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._cancel_save_problem()
                    continue
                self.save_description_input.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dialog = self._save_dialog_rect()
                    save_rect = pygame.Rect(dialog.x + dialog.width - 280, dialog.bottom - 64, 130, 46)
                    cancel_rect = pygame.Rect(dialog.x + dialog.width - 140, dialog.bottom - 64, 120, 46)
                    if save_rect.collidepoint(event.pos):
                        self._confirm_save_problem()
                    elif cancel_rect.collidepoint(event.pos):
                        self._cancel_save_problem()
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_VISUALIZER:
                        self._back_from_visualizer()
                    elif self.state != STATE_MAIN_MENU:
                        self.set_state(STATE_MAIN_MENU)
                elif self.state == STATE_VISUALIZER:
                    if event.key == pygame.K_RIGHT:
                        self._step_fwd()
                    elif event.key == pygame.K_LEFT:
                        self._step_back()
                    elif event.key == pygame.K_SPACE:
                        self._toggle_play()

            # Preset and move-log scrollbars need first chance to consume mouse input.
            consumed = False
            if self.state == STATE_PRESET_SETUP:
                consumed = self._handle_preset_events(event)
            elif self.state == STATE_VISUALIZER:
                consumed = self.move_log.handle_event(event)
            elif self.state == STATE_PLAY:
                consumed = self._play_handle_event(event)
            if consumed:
                continue

            for btn in self.buttons:
                btn.handle_event(event)

            if self.state == STATE_CLASSIC_SETUP:
                self.classic_n_input.handle_event(event)
                for b in getattr(self, "classic_start_buttons", []):
                    b.handle_event(event)
                for b in getattr(self, "classic_target_buttons", []):
                    b.handle_event(event)
            elif self.state == STATE_CUSTOM_SETUP:
                for rod in (1, 2, 3):
                    self.custom_inputs[rod].handle_event(event)
                for b in getattr(self, "custom_target_buttons", []):
                    b.handle_event(event)
            elif self.state == STATE_PLAY_SETUP:
                for rod in (1, 2, 3):
                    self.play_setup_inputs[rod].handle_event(event)
                for b in getattr(self, "play_target_buttons", []):
                    b.handle_event(event)

    def _handle_preset_events(self, event):
        mouse_pos = event.pos if hasattr(event, "pos") else pygame.mouse.get_pos()
        max_scroll, bar_rect = self._preset_scroll_metrics()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if bar_rect and bar_rect.inflate(8, 4).collidepoint(mouse_pos):
                self.preset_dragging_scrollbar = True
                self._preset_drag_offset_y = mouse_pos[1] - bar_rect.y
                return True
            if self.preset_list_rect.collidepoint(mouse_pos):
                row_h = 74
                rel_y = mouse_pos[1] - self.preset_list_rect.y + self.preset_scroll
                idx = rel_y // row_h
                keys = list(self.problems.keys())
                if 0 <= idx < len(keys):
                    self.preset_selected = keys[idx]
                    self.build_preset_setup()
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_dragging = self.preset_dragging_scrollbar
            self.preset_dragging_scrollbar = False
            return was_dragging
        elif event.type == pygame.MOUSEMOTION and self.preset_dragging_scrollbar and bar_rect:
            rect = self.preset_list_rect
            bar_h = bar_rect.height
            travel = max(1, rect.height - bar_h)
            new_bar_y = clamp(
                mouse_pos[1] - self._preset_drag_offset_y,
                rect.y,
                rect.bottom - bar_h,
            )
            ratio = (new_bar_y - rect.y) / travel
            self.preset_scroll = int(round(ratio * max_scroll))
            return True
        elif event.type == pygame.MOUSEWHEEL and self.preset_list_rect.collidepoint(mouse_pos):
            self.preset_scroll = clamp(
                self.preset_scroll - event.y * 40, 0, max_scroll
            )
            return True
        return False

    # ---------------------------- update ----------------------------

    def _update(self, dt):
        for btn in self.buttons:
            btn.update(dt)

        if self.state == STATE_CLASSIC_SETUP:
            self.classic_n_input.update(dt)
        elif self.state == STATE_CUSTOM_SETUP:
            for rod in (1, 2, 3):
                self.custom_inputs[rod].update(dt)
        elif self.state == STATE_PLAY_SETUP:
            for rod in (1, 2, 3):
                self.play_setup_inputs[rod].update(dt)
        elif self.state == STATE_VISUALIZER and self.save_dialog_open:
            self.save_description_input.update(dt)

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.error_message = None
                self.info_message = None

        if self.state == STATE_VISUALIZER:
            self.scene.update(dt)
            if self.save_feedback_timer > 0:
                self.save_feedback_timer -= dt
                if self.save_feedback_timer <= 0:
                    self.save_feedback = None
            if self.verify_feedback_timer > 0:
                self.verify_feedback_timer -= dt
                if self.verify_feedback_timer <= 0:
                    self.verify_feedback = None

            if self.auto_play and not self.scene.is_animating():
                self.auto_timer -= dt
                if self.auto_timer <= 0:
                    if self.move_index < len(self.seq):
                        self._step_fwd()
                        self.auto_timer = 0.08  # small gap between auto moves
                    else:
                        self.auto_play = False

            # update play button label
            if self.move_index >= len(self.seq):
                self.btn_play.label = "Replay"
            else:
                self.btn_play.label = "Pause" if self.auto_play else "Play"

            self.btn_step_fwd.enabled = self._can_step_fwd()
            self.btn_step_back.enabled = self._can_step_back()

        elif self.state == STATE_PLAY:
            self.play_scene.update(dt)
            if self.play_running and not self.play_solved:
                self.play_elapsed += dt
            if self.play_invalid_flash_timer > 0:
                self.play_invalid_flash_timer -= dt
                if self.play_invalid_flash_timer <= 0:
                    self.play_invalid_flash_timer = 0.0
                    self.play_invalid_flash_rod = None

    # ---------------------------- draw ----------------------------

    def _draw(self):
        surf = self.screen
        vertical_gradient(surf, BG_TOP, BG_BOTTOM)

        if self.state == STATE_MAIN_MENU:
            self._draw_main_menu(surf)
        elif self.state == STATE_CLASSIC_SETUP:
            self._draw_classic_setup(surf)
        elif self.state == STATE_CUSTOM_SETUP:
            self._draw_custom_setup(surf)
        elif self.state == STATE_PRESET_SETUP:
            self._draw_preset_setup(surf)
        elif self.state == STATE_VISUALIZER:
            self._draw_visualizer(surf)
        elif self.state == STATE_PLAY_SETUP:
            self._draw_play_setup(surf)
        elif self.state == STATE_PLAY:
            self._draw_play(surf)

        for btn in self.buttons:
            btn.draw(surf)

        if self.state == STATE_VISUALIZER and self.save_dialog_open:
            self._draw_save_dialog(surf)

        self._draw_messages(surf)

    def _draw_header(self, surf, title, subtitle=None):
        w = surf.get_width()
        title_surf = self.font_title.render(title, True, TEXT_MAIN)
        surf.blit(title_surf, title_surf.get_rect(centerx=w // 2, top=36))
        if subtitle:
            sub_surf = self.font_body.render(subtitle, True, TEXT_DIM)
            surf.blit(
                sub_surf,
                sub_surf.get_rect(centerx=w // 2, top=36 + title_surf.get_height() + 6),
            )

    def _draw_main_menu(self, surf):
        self._draw_header(
            surf, "Tower of Hanoi", "Choose how you'd like to set up the puzzle"
        )
        # decorative mini hanoi icon, anchored to the bottom of the window
        deco_bottom = surf.get_height() - 46
        self._draw_decorative_towers(surf, deco_bottom)

    def _draw_decorative_towers(self, surf, base_y):
        w = surf.get_width()
        cx = w // 2
        rod_h = 62
        spacing = 90
        cols_x = [cx - spacing, cx, cx + spacing]
        for x in cols_x:
            pygame.draw.rect(
                surf, ROD_COLOR, (x - 3, base_y - rod_h, 6, rod_h), border_radius=3
            )
            pygame.draw.circle(surf, ROD_HIGHLIGHT, (x, base_y - rod_h), 5)
        pygame.draw.rect(
            surf,
            WOOD_DARK,
            (cx - spacing - 60, base_y, spacing * 2 + 120, 12),
            border_radius=6,
        )

        stack = [3, 2, 1]  # bottom to top on the left rod
        for i, ring_id in enumerate(stack):
            color = RING_PALETTE[(ring_id - 1) % len(RING_PALETTE)]
            w_ring = 34 + (3 - ring_id) * 22
            rect = pygame.Rect(0, 0, w_ring, 15)
            rect.center = (cols_x[0], base_y - 7 - i * 16)
            rounded_rect(
                surf, rect, color, radius=7, border_color=(20, 20, 25), border_width=2
            )

    def _draw_classic_setup(self, surf):
        self._draw_header(surf, "Classic Mode", "All rings start on one rod")
        cx = surf.get_width() // 2
        panel_w = 560
        left = cx - panel_w // 2
        y = 250

        label = self.font_body_bold.render("Number of rings:", True, TEXT_MAIN)
        surf.blit(label, (left, y + 10))
        self.classic_n_input.draw(surf)

        rod_y = y + 90
        label = self.font_body_bold.render("Starting rod:", True, TEXT_MAIN)
        surf.blit(label, (left, rod_y + 10))
        for b in self.classic_start_buttons:
            b.draw(surf)

        target_y = rod_y + 90
        label = self.font_body_bold.render("Target rod:", True, TEXT_MAIN)
        surf.blit(label, (left, target_y + 10))
        for b in self.classic_target_buttons:
            b.draw(surf)

        hint_y = target_y + 90 + 66
        hint = self.font_small.render(
            "Tip: up to 16 rings supported for a clean visualization.", True, TEXT_FAINT
        )
        surf.blit(hint, hint.get_rect(centerx=cx, top=hint_y + 30))

    def _draw_custom_setup(self, surf):
        self._draw_header(
            surf,
            "Custom Mode",
            "Specify rings per rod (bottom to top, comma-separated)",
        )
        cx = surf.get_width() // 2
        panel_w = 640
        left = cx - panel_w // 2
        y = 210
        row_h = 64
        for i, rod in enumerate((1, 2, 3)):
            label = self.font_body_bold.render(f"Rod {rod}:", True, TEXT_MAIN)
            surf.blit(label, (left, y + i * row_h + 10))
            self.custom_inputs[rod].draw(surf)

        target_y = y + 3 * row_h + 20
        label = self.font_body_bold.render("Target rod:", True, TEXT_MAIN)
        surf.blit(label, (left, target_y + 10))
        for b in self.custom_target_buttons:
            b.draw(surf)

        hint_y = target_y + 90 + 66
        hint1 = self.font_small.render(
            "Example: '3, 2, 1' means ring 3 at bottom, ring 1 on top. Leave blank for an empty rod.",
            True,
            TEXT_FAINT,
        )
        surf.blit(hint1, hint1.get_rect(centerx=cx, top=hint_y + 20))
        hint2 = self.font_small.render(
            "Rings across all rods must be exactly 1..N with no repeats, largest at bottom.",
            True,
            TEXT_FAINT,
        )
        surf.blit(hint2, hint2.get_rect(centerx=cx, top=hint_y + 44))

    def _draw_play_setup(self, surf):
        self._draw_header(
            surf,
            "Play Mode",
            "Set up a puzzle, then solve it yourself by hand",
        )
        cx = surf.get_width() // 2
        panel_w = 640
        left = cx - panel_w // 2
        y = 210
        row_h = 64
        for i, rod in enumerate((1, 2, 3)):
            label = self.font_body_bold.render(f"Rod {rod}:", True, TEXT_MAIN)
            surf.blit(label, (left, y + i * row_h + 10))
            self.play_setup_inputs[rod].draw(surf)

        target_y = y + 3 * row_h + 20
        label = self.font_body_bold.render("Target rod:", True, TEXT_MAIN)
        surf.blit(label, (left, target_y + 10))
        for b in self.play_target_buttons:
            b.draw(surf)

        hint_y = target_y + 90 + 66
        hint1 = self.font_small.render(
            "Example: '3, 2, 1' means ring 3 at bottom, ring 1 on top. Leave blank for an empty rod.",
            True,
            TEXT_FAINT,
        )
        surf.blit(hint1, hint1.get_rect(centerx=cx, top=hint_y + 20))
        hint2 = self.font_small.render(
            "Rings across all rods must be exactly 1..N with no repeats, largest at bottom.",
            True,
            TEXT_FAINT,
        )
        surf.blit(hint2, hint2.get_rect(centerx=cx, top=hint_y + 44))
        hint3 = self.font_small.render(
            "Goal: move every ring onto the target rod. Drag rings, or click a rod then another to move.",
            True,
            TEXT_FAINT,
        )
        surf.blit(hint3, hint3.get_rect(centerx=cx, top=hint_y + 68))

    def _draw_preset_setup(self, surf):
        builtin_count = 0
        try:
            with open("problems.json", "r") as f:
                builtin_count = len(json.load(f).get("problems", {}))
        except Exception:
            pass
        saved_count = max(0, len(self.problems) - builtin_count)
        self._draw_header(
            surf,
            "Preset Problems",
            f"{builtin_count} built-in puzzle(s) + {saved_count} saved puzzle(s)",
        )
        rect = self.preset_list_rect
        rounded_rect(
            surf, rect, PANEL_BG, radius=14, border_color=PANEL_BORDER, border_width=2
        )

        clip = rect.inflate(-8, -8)
        old_clip = surf.get_clip()
        surf.set_clip(clip)

        row_h = 74
        keys = list(self.problems.keys())
        for idx, key in enumerate(keys):
            row_y = clip.y + idx * row_h - self.preset_scroll
            if row_y + row_h < clip.y or row_y > clip.bottom:
                continue
            problem = self.problems[key]
            row_rect = pygame.Rect(clip.x + 4, row_y + 4, clip.width - 8, row_h - 8)
            selected = key == self.preset_selected
            bg = PANEL_BG_LIGHT if selected else PANEL_BG
            border = ACCENT if selected else PANEL_BORDER
            rounded_rect(
                surf,
                row_rect,
                bg,
                radius=10,
                border_color=border,
                border_width=2 if selected else 1,
            )

            num_surf = self.font_h2.render(
                f"#{key}", True, ACCENT_2 if selected else TEXT_DIM
            )
            surf.blit(
                num_surf,
                (
                    row_rect.x + 16,
                    row_rect.y + row_rect.height // 2 - num_surf.get_height() // 2,
                ),
            )

            desc_surf = self.font_body_bold.render(
                problem["description"], True, TEXT_MAIN
            )
            surf.blit(desc_surf, (row_rect.x + 90, row_rect.y + 10))

            r1 = problem["initial_state"]["1"]
            r2 = problem["initial_state"]["2"]
            r3 = problem["initial_state"]["3"]
            detail = (
                f"Rod1={r1}  Rod2={r2}  Rod3={r3}  ->  target rod {problem['target']}"
            )
            detail_surf = self.font_small.render(detail, True, TEXT_DIM)
            surf.blit(detail_surf, (row_rect.x + 90, row_rect.y + 38))

        surf.set_clip(old_clip)

        # draggable scrollbar
        _, bar_rect = self._preset_scroll_metrics()
        if bar_rect:
            track_rect = pygame.Rect(rect.right - 14, rect.y, 10, rect.height)
            rounded_rect(surf, track_rect, PANEL_BG_LIGHT, radius=5)
            rounded_rect(
                surf,
                bar_rect,
                shade(ACCENT, 1.0) if self.preset_dragging_scrollbar else ACCENT_DIM,
                radius=5,
            )

    def _draw_visualizer(self, surf):
        w = surf.get_width()
        title = (
            f"Rod {self._start_rod_display()} -> Rod {self.target}"
            if self.rods
            else "Visualizer"
        )
        title_surf = self.font_h2.render(title, True, TEXT_MAIN)
        surf.blit(title_surf, (24, 30))

        moves_text = (
            f"{self.n_total} rings   •   {len(self.seq)} total moves   •   optimal <= {2**self.n_total - 1}"
            if self.seq is not None
            else ""
        )
        info_surf = self.font_body.render(moves_text, True, TEXT_DIM)
        surf.blit(info_surf, info_surf.get_rect(right=w - 24, top=38))

        self.scene.draw(surf, self.font_ring)
        self.move_log.draw(surf)

        # speed label between +/- buttons
        speed_label = self.font_body_bold.render(
            self.speed_labels[self.speed_index], True, TEXT_MAIN
        )
        surf.blit(
            speed_label,
            speed_label.get_rect(
                centerx=self.speed_label_center_x, centery=self.speed_label_center_y
            ),
        )

        if self.solved_complete and self.seq is not None:
            done_surf = self.font_body_bold.render(
                "Solved! All rings moved to the target rod.", True, SUCCESS
            )
            surf.blit(
                done_surf,
                done_surf.get_rect(
                    centerx=(self.scene.area.x + self.scene.area.width // 2),
                    bottom=self.scene.area.y + 4,
                ),
            )

        # save/verify feedback toast, anchored just above the control bar
        toast_y = self.control_bar_top_y - 40
        if self.save_feedback:
            color = SUCCESS if "Saved" in self.save_feedback else ERROR
            t = self.font_body_bold.render(self.save_feedback, True, color)
            surf.blit(t, t.get_rect(right=w - 24, top=toast_y))
        if self.verify_feedback:
            color = SUCCESS if "Valid" in self.verify_feedback else ERROR
            t = self.font_body_bold.render(self.verify_feedback, True, color)
            surf.blit(t, t.get_rect(right=w - 24, top=toast_y))

    def _format_time(self, seconds):
        seconds = max(0, seconds)
        m = int(seconds) // 60
        s = seconds - m * 60
        return f"{m:02d}:{s:05.2f}"

    def _draw_play(self, surf):
        w = surf.get_width()
        title = f"Play Mode — reach Rod {self.play_target}" if self.play_target else "Play Mode"
        title_surf = self.font_h2.render(title, True, TEXT_MAIN)
        surf.blit(title_surf, (24, 30))

        # HUD: timer + move counter, top-right.
        timer_str = self._format_time(self.play_elapsed)
        timer_color = SUCCESS if self.play_solved else TEXT_MAIN
        timer_surf = self.font_h2.render(timer_str, True, timer_color)
        surf.blit(timer_surf, timer_surf.get_rect(right=w - 24, top=26))
        moves_label = f"Moves: {self.play_move_count}"
        moves_surf = self.font_body.render(moves_label, True, TEXT_DIM)
        surf.blit(
            moves_surf,
            moves_surf.get_rect(right=w - 24, top=26 + timer_surf.get_height() + 4),
        )

        # Highlight the selected rod (click-to-select) with a soft glow band
        # behind it, and flash red briefly over an invalid target rod.
        scene = self.play_scene
        if self.play_selected_rod is not None:
            x = scene.rod_x[self.play_selected_rod]
            band = pygame.Rect(0, 0, scene.max_ring_w + 40, scene.rod_height + 40)
            band.center = (int(x), int((scene.rod_top_y + scene.base_y) / 2))
            glow = pygame.Surface(band.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*ACCENT, 40), glow.get_rect(), border_radius=24)
            pygame.draw.rect(glow, (*ACCENT, 130), glow.get_rect(), width=3, border_radius=24)
            surf.blit(glow, band.topleft)
        if self.play_invalid_flash_rod is not None and self.play_invalid_flash_timer > 0:
            x = scene.rod_x[self.play_invalid_flash_rod]
            t = clamp(self.play_invalid_flash_timer / 0.35, 0.0, 1.0)
            fill_alpha = int(30 * t)
            border_alpha = int(190 * t)
            band = pygame.Rect(0, 0, scene.max_ring_w + 40, scene.rod_height + 40)
            band.center = (int(x), int((scene.rod_top_y + scene.base_y) / 2))
            glow = pygame.Surface(band.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*ERROR, fill_alpha), glow.get_rect(), border_radius=24)
            pygame.draw.rect(glow, (*ERROR, border_alpha), glow.get_rect(), width=3, border_radius=24)
            surf.blit(glow, band.topleft)

        scene.draw(surf, self.font_ring)

        hint = "Drag a ring, or click a rod to select it and click another rod to move there."
        hint_surf = self.font_small.render(hint, True, TEXT_FAINT)
        surf.blit(hint_surf, hint_surf.get_rect(centerx=scene.area.centerx, top=scene.area.y - 30))

        if self.play_solved:
            optimal = self.play_optimal_moves
            extra = self.play_move_count - optimal
            if extra <= 0:
                verdict = "Optimal! You matched the best possible solution."
            else:
                verdict = f"Solved in {extra} move{'s' if extra != 1 else ''} more than optimal ({optimal})."
            lines = [
                "Solved!",
                f"Time: {self._format_time(self.play_elapsed)}   Moves: {self.play_move_count}",
                verdict,
            ]
            panel_w2 = 520
            panel_h2 = 130
            panel_rect = pygame.Rect(0, 0, panel_w2, panel_h2)
            panel_rect.center = (scene.area.centerx, scene.area.y + 90)
            rounded_rect(
                surf, panel_rect, PANEL_BG_LIGHT, radius=16,
                border_color=SUCCESS, border_width=2,
            )
            ly = panel_rect.y + 16
            for i, line in enumerate(lines):
                font = self.font_h2 if i == 0 else self.font_body
                color = SUCCESS if i == 0 else TEXT_MAIN
                line_surf = font.render(line, True, color)
                surf.blit(line_surf, line_surf.get_rect(centerx=panel_rect.centerx, top=ly))
                ly += line_surf.get_height() + 6

    def _save_dialog_rect(self):
        rect = pygame.Rect(0, 0, SAVE_DIALOG_W, SAVE_DIALOG_H)
        rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        return rect

    def _draw_save_dialog(self, surf):
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surf.blit(overlay, (0, 0))

        rect = self._save_dialog_rect()
        rounded_rect(
            surf, rect, PANEL_BG, radius=16, border_color=ACCENT, border_width=2
        )
        title = self.font_h2.render("Save Problem", True, TEXT_MAIN)
        surf.blit(title, (rect.x + 28, rect.y + 22))
        prompt = self.font_small.render(
            "Enter a description; this problem will appear in Preset Problems.",
            True,
            TEXT_DIM,
        )
        surf.blit(prompt, (rect.x + 28, rect.y + 66))

        self.save_description_input.rect = pygame.Rect(
            rect.x + 28, rect.y + 105, rect.width - 56, 52
        )
        self.save_description_input.draw(surf)

        if getattr(self, "save_dialog_error", None):
            err = self.font_small.render(self.save_dialog_error, True, ERROR)
            surf.blit(err, (rect.x + 28, rect.y + 164))

        save_rect = pygame.Rect(rect.x + rect.width - 280, rect.bottom - 64, 130, 46)
        cancel_rect = pygame.Rect(rect.x + rect.width - 140, rect.bottom - 64, 120, 46)
        rounded_rect(surf, save_rect, ACCENT, radius=10)
        rounded_rect(surf, cancel_rect, PANEL_BG_LIGHT, radius=10, border_color=PANEL_BORDER, border_width=2)
        save_txt = self.font_body_bold.render("Save", True, (18, 20, 30))
        cancel_txt = self.font_body_bold.render("Cancel", True, TEXT_MAIN)
        surf.blit(save_txt, save_txt.get_rect(center=save_rect.center))
        surf.blit(cancel_txt, cancel_txt.get_rect(center=cancel_rect.center))

    def _start_rod_display(self):
        for rod, stack in self.rods.items():
            if stack:
                return rod
        return "?"

    def _draw_messages(self, surf):
        if self.error_message:
            self._draw_toast(surf, self.error_message, ERROR)
        elif self.info_message:
            self._draw_toast(surf, self.info_message, SUCCESS)

    def _draw_toast(self, surf, text, color):
        w = surf.get_width()
        txt_surf = self.font_body_bold.render(text, True, (20, 20, 25))
        pad_x, pad_y = 20, 12
        box_w = txt_surf.get_width() + pad_x * 2
        box_h = txt_surf.get_height() + pad_y * 2
        rect = pygame.Rect(0, 0, box_w, box_h)
        rect.centerx = w // 2
        rect.top = 100
        alpha = (
            clamp(self.message_timer / 0.4, 0.0, 1.0)
            if self.message_timer < 0.4
            else 1.0
        )
        toast_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        rounded_rect(
            toast_surf, toast_surf.get_rect(), (*color, int(255 * alpha)), radius=10
        )
        surf.blit(toast_surf, rect.topleft)
        txt_surf.set_alpha(int(255 * alpha))
        surf.blit(txt_surf, (rect.x + pad_x, rect.y + pad_y))


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = HanoiApp()
    app.run()


if __name__ == "__main__":
    main()
