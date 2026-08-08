"""Reusable browser-side interactive waveform component."""

import base64
from typing import Any

import streamlit as st

from audio_chopper import WaveformData


WAVEFORM_HTML = """
<div class="wave-editor">
    <canvas aria-label="Interactive audio waveform"></canvas>
    <audio preload="auto"></audio>
    <div class="wave-toolbar">
        <button type="button" data-action="play">▶ PLAY SELECTION</button>
        <button type="button" data-action="stop">■ STOP</button>
        <button type="button" data-action="loop" aria-pressed="false">↻ LOOP OFF</button>
        <span class="selection-time"></span>
        <button type="button" class="apply" data-action="apply">USE SELECTION</button>
    </div>
    <div class="wave-hint">DRAG TO SELECT · WHEEL TO ZOOM · SHIFT + WHEEL TO MOVE</div>
</div>
"""

WAVEFORM_CSS = """
.wave-editor {
    position: relative;
    overflow: hidden;
    padding: 12px 12px 8px;
    border: 1px solid rgba(216, 195, 154, 0.20);
    border-radius: 15px 6px 15px 6px;
    background: rgba(8, 17, 13, 0.84);
    user-select: none;
}
canvas {
    display: block;
    width: 100%;
    height: 210px;
    cursor: crosshair;
    touch-action: none;
}
.wave-hint {
    padding-top: 7px;
    color: rgba(216, 195, 154, 0.58);
    font: 600 10px "IBM Plex Mono", monospace;
    letter-spacing: 0.10em;
    text-align: right;
}
.wave-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-top: 9px;
}
.wave-toolbar button {
    min-height: 32px;
    padding: 0 11px;
    border: 1px solid rgba(216,195,154,.22);
    border-radius: 7px 3px 7px 3px;
    background: rgba(16,39,27,.88);
    color: #d8c39a;
    font: 700 10px Inter, sans-serif;
    letter-spacing: .06em;
    cursor: pointer;
}
.wave-toolbar button:hover { border-color: #b8ff3d; color: #f1e9d5; }
.wave-toolbar button.loop-active { border-color:#ffb23f; color:#ffb23f; background:rgba(255,178,63,.10); }
.wave-toolbar button.apply { margin-left: auto; border-color: #b8ff3d; background: #b8ff3d; color: #08110d; }
.selection-time { color:#b8ff3d; font:600 11px "IBM Plex Mono",monospace; }
audio { display:none; }
"""

WAVEFORM_JS = """
export default function(component) {
    const { data, parentElement, setStateValue } = component;
    const canvas = parentElement.querySelector('canvas');
    const context = canvas.getContext('2d');
    const audio = parentElement.querySelector('audio');
    const timeLabel = parentElement.querySelector('.selection-time');
    const playButton = parentElement.querySelector('[data-action="play"]');
    const stopButton = parentElement.querySelector('[data-action="stop"]');
    const loopButton = parentElement.querySelector('[data-action="loop"]');
    const applyButton = parentElement.querySelector('[data-action="apply"]');
    audio.src = data.audio_url;
    const peaks = data.peaks;
    const duration = data.duration;
    let start = data.selection.start;
    let end = data.selection.end;
    let viewStart = data.view.start;
    let viewEnd = data.view.end;
    let dragMode = null;
    let anchorTime = 0;
    let originalStart = start;
    let originalEnd = end;
    let playingSelection = false;
    let loopSelection = false;
    let playheadTime = null;
    let animationFrame = null;

    function clamp(value, minimum, maximum) {
        return Math.max(minimum, Math.min(maximum, value));
    }

    function timeAt(clientX) {
        const bounds = canvas.getBoundingClientRect();
        const ratio = clamp((clientX - bounds.left) / bounds.width, 0, 1);
        return viewStart + ratio * (viewEnd - viewStart);
    }

    function xAt(time, width) {
        return (time - viewStart) / (viewEnd - viewStart) * width;
    }

    function resize() {
        const ratio = window.devicePixelRatio || 1;
        const bounds = canvas.getBoundingClientRect();
        canvas.width = Math.max(1, Math.round(bounds.width * ratio));
        canvas.height = Math.max(1, Math.round(bounds.height * ratio));
        draw();
    }

    function drawWave(width, height, color, clipStart, clipEnd) {
        const first = Math.max(0, Math.floor(viewStart / duration * peaks.length));
        const last = Math.min(peaks.length, Math.ceil(viewEnd / duration * peaks.length));
        const visible = Math.max(1, last - first);
        const middle = height / 2;
        const amplitude = height * 0.43;
        context.save();
        if (clipStart !== undefined) {
            context.beginPath();
            context.rect(clipStart, 0, Math.max(0, clipEnd - clipStart), height);
            context.clip();
        }
        context.strokeStyle = color;
        context.lineWidth = Math.max(1, window.devicePixelRatio || 1);
        context.beginPath();
        for (let pixel = 0; pixel < width; pixel += 2) {
            const from = first + Math.floor(pixel / width * visible);
            const to = Math.min(last, first + Math.ceil((pixel + 2) / width * visible));
            let peak = 0;
            for (let index = from; index < to; index++) peak = Math.max(peak, peaks[index] || 0);
            context.moveTo(pixel, middle - peak * amplitude);
            context.lineTo(pixel, middle + peak * amplitude);
        }
        context.stroke();
        context.restore();
    }

    function draw() {
        const width = canvas.width;
        const height = canvas.height;
        context.clearRect(0, 0, width, height);
        context.fillStyle = '#08110d';
        context.fillRect(0, 0, width, height);
        context.strokeStyle = 'rgba(216,195,154,.12)';
        context.beginPath();
        context.moveTo(0, height / 2);
        context.lineTo(width, height / 2);
        context.stroke();
        drawWave(width, height, 'rgba(216,195,154,.38)');

        const selectedX1 = xAt(start, width);
        const selectedX2 = xAt(end, width);
        context.fillStyle = 'rgba(31,107,69,.18)';
        context.fillRect(selectedX1, 0, selectedX2 - selectedX1, height);
        drawWave(width, height, '#b8ff3d', selectedX1, selectedX2);
        context.strokeStyle = '#f1e9d5';
        context.lineWidth = 2 * (window.devicePixelRatio || 1);
        context.beginPath();
        context.moveTo(selectedX1, 0);
        context.lineTo(selectedX1, height);
        context.moveTo(selectedX2, 0);
        context.lineTo(selectedX2, height);
        context.stroke();

        if (playheadTime !== null && playheadTime >= viewStart && playheadTime <= viewEnd) {
            const playheadX = xAt(playheadTime, width);
            context.strokeStyle = '#ffb23f';
            context.lineWidth = 2 * (window.devicePixelRatio || 1);
            context.beginPath();
            context.moveTo(playheadX, 0);
            context.lineTo(playheadX, height);
            context.stroke();
            context.fillStyle = '#ffb23f';
            context.beginPath();
            context.moveTo(playheadX - 5, 0);
            context.lineTo(playheadX + 5, 0);
            context.lineTo(playheadX, 8 * (window.devicePixelRatio || 1));
            context.fill();
        }

        context.fillStyle = '#d8c39a';
        context.font = `${11 * (window.devicePixelRatio || 1)}px IBM Plex Mono, monospace`;
        context.fillText(viewStart.toFixed(2) + ' s', 8, height - 10);
        const endLabel = viewEnd.toFixed(2) + ' s';
        const labelWidth = context.measureText(endLabel).width;
        context.fillText(endLabel, width - labelWidth - 8, height - 10);
        timeLabel.textContent = `${start.toFixed(2)} — ${end.toFixed(2)} s`;
    }

    function commitSelection() {
        if (end - start < 0.1) end = Math.min(duration, start + 0.1);
        setStateValue('selection', {
            start,
            end,
            view_start: viewStart,
            view_end: viewEnd,
        });
    }

    canvas.onpointerdown = (event) => {
        canvas.setPointerCapture(event.pointerId);
        const time = timeAt(event.clientX);
        const tolerance = (viewEnd - viewStart) * 0.025;
        originalStart = start;
        originalEnd = end;
        anchorTime = time;
        if (Math.abs(time - start) <= tolerance) dragMode = 'start';
        else if (Math.abs(time - end) <= tolerance) dragMode = 'end';
        else if (time > start && time < end) dragMode = 'move';
        else {
            dragMode = 'new';
            start = time;
            end = Math.min(viewEnd, time + 0.1);
        }
        draw();
    };

    canvas.onpointermove = (event) => {
        if (!dragMode) return;
        const time = timeAt(event.clientX);
        if (dragMode === 'start') start = clamp(time, viewStart, end - 0.1);
        else if (dragMode === 'end') end = clamp(time, start + 0.1, viewEnd);
        else if (dragMode === 'move') {
            const length = originalEnd - originalStart;
            const nextStart = clamp(originalStart + time - anchorTime, viewStart, viewEnd - length);
            start = nextStart;
            end = nextStart + length;
        } else {
            start = Math.min(anchorTime, time);
            end = Math.max(anchorTime, time);
        }
        draw();
    };

    canvas.onpointerup = (event) => {
        if (!dragMode) return;
        canvas.releasePointerCapture(event.pointerId);
        dragMode = null;
        draw();
    };

    canvas.onwheel = (event) => {
        event.preventDefault();
        const oldSpan = viewEnd - viewStart;
        if (event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
            const direction = event.deltaX || event.deltaY;
            const shift = oldSpan * 0.16 * Math.sign(direction);
            viewStart = clamp(viewStart + shift, 0, duration - oldSpan);
            viewEnd = viewStart + oldSpan;
        } else {
            const anchor = timeAt(event.clientX);
            const newSpan = clamp(oldSpan * (event.deltaY < 0 ? 0.72 : 1.38), 0.25, duration);
            const ratio = (anchor - viewStart) / oldSpan;
            viewStart = clamp(anchor - newSpan * ratio, 0, duration - newSpan);
            viewEnd = viewStart + newSpan;
        }
        draw();
    };

    playButton.onclick = () => {
        playingSelection = true;
        audio.currentTime = start;
        playheadTime = start;
        audio.play();
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
        animatePlayhead();
    };
    stopButton.onclick = () => {
        playingSelection = false;
        audio.pause();
        playheadTime = start;
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
        animationFrame = null;
        draw();
    };
    loopButton.onclick = () => {
        loopSelection = !loopSelection;
        loopButton.classList.toggle('loop-active', loopSelection);
        loopButton.setAttribute('aria-pressed', String(loopSelection));
        loopButton.textContent = loopSelection ? '↻ LOOP ON' : '↻ LOOP OFF';
    };
    applyButton.onclick = () => commitSelection();
    audio.ontimeupdate = () => {
        if (playingSelection && audio.currentTime >= end) {
            if (loopSelection) {
                audio.currentTime = start;
                playheadTime = start;
                audio.play();
            } else {
                playingSelection = false;
                audio.pause();
                audio.currentTime = start;
                playheadTime = start;
                if (animationFrame !== null) cancelAnimationFrame(animationFrame);
                animationFrame = null;
                draw();
            }
        }
    };

    function animatePlayhead() {
        if (!playingSelection) return;
        if (audio.currentTime >= end && loopSelection) audio.currentTime = start;
        playheadTime = audio.currentTime;
        draw();
        animationFrame = requestAnimationFrame(animatePlayhead);
    }

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    resize();
    return () => {
        observer.disconnect();
        audio.pause();
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
    };
}
"""


_interactive_waveform = st.components.v2.component(
    "vibes_supplier_waveform",
    html=WAVEFORM_HTML,
    css=WAVEFORM_CSS,
    js=WAVEFORM_JS,
)


def interactive_waveform(
    waveform: WaveformData,
    selection: tuple[float, float],
    view: tuple[float, float],
    browser_audio: bytes,
) -> dict[str, float]:
    """Render the browser waveform and return committed selection state."""
    default = {
        "selection": {
            "start": selection[0],
            "end": selection[1],
            "view_start": view[0],
            "view_end": view[1],
        }
    }
    result = _interactive_waveform(
        key="audio_chopper_interactive_waveform",
        data={
            "peaks": waveform.peaks,
            "duration": waveform.duration_seconds,
            "selection": {"start": selection[0], "end": selection[1]},
            "view": {"start": view[0], "end": view[1]},
            "audio_url": (
                "data:audio/mpeg;base64,"
                + base64.b64encode(browser_audio).decode("ascii")
            ),
        },
        default=default,
        height=260,
        on_selection_change=lambda: None,
    )
    value: Any = getattr(result, "selection", None)
    return value or default["selection"]
