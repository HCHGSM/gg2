import os
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QVariantAnimation, QSequentialAnimationGroup, QParallelAnimationGroup, QPoint, QRectF
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QProgressBar, QFrame
from PySide6.QtGui import QColor, QPainter, QPainterPath
import random

# Global setting, could be linked to DB Setting table in future
ANIMATION_LEVEL = "HIGH" 

class Animations:
    @staticmethod
    def _is_enabled():
        return ANIMATION_LEVEL != "OFF"

    @staticmethod
    def apply_glow(widget, color="#6366F1", radius=30, alpha=80):
        if not Animations._is_enabled(): return
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(radius)
        shadow.setColor(QColor(QColor(color).red(), QColor(color).green(), QColor(color).blue(), alpha))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def apply_soft_shadow(widget):
        if not Animations._is_enabled(): return
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 15)
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def fade_in(widget, duration=600, easing=QEasingCurve.OutCubic, delay=0):
        if not Animations._is_enabled():
            widget.show()
            return
            
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        def start_anim():
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(easing)
            anim.start(QPropertyAnimation.DeleteWhenStopped)
            widget._fade_anim = anim 
            
        if delay > 0:
            QTimer.singleShot(delay, start_anim)
        else:
            start_anim()

    @staticmethod
    def fade_out(widget, duration=400, on_finished=None):
        if not Animations._is_enabled():
            if on_finished: on_finished()
            return
            
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        if on_finished:
            anim.finished.connect(on_finished)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        widget._fade_anim = anim

    @staticmethod
    def pop_in(widget, duration=600, delay=0):
        if not Animations._is_enabled():
            widget.show()
            return
            
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(0)
        widget.setGraphicsEffect(effect)
        
        def start_anim():
            anim_op = QPropertyAnimation(effect, b"opacity")
            anim_op.setDuration(duration)
            anim_op.setStartValue(0.0)
            anim_op.setEndValue(1.0)
            anim_op.setEasingCurve(QEasingCurve.OutQuart)
            
            anim_pos = QPropertyAnimation(widget, b"pos")
            anim_pos.setDuration(duration)
            anim_pos.setStartValue(widget.pos() + QPoint(0, 30))
            anim_pos.setEndValue(widget.pos())
            anim_pos.setEasingCurve(QEasingCurve.OutBack)
            
            group = QParallelAnimationGroup(widget)
            group.addAnimation(anim_op)
            group.addAnimation(anim_pos)
            group.start(QPropertyAnimation.DeleteWhenStopped)
            widget._pop_anim = group
            
        if delay > 0:
            QTimer.singleShot(delay, start_anim)
        else:
            start_anim()

    @staticmethod
    def count_number(label, start_val, end_val, is_float=True, prefix="", suffix="", duration=1500):
        if not Animations._is_enabled():
            if is_float: label.setText(f"{prefix}{end_val:,.2f}{suffix}")
            else: label.setText(f"{prefix}{int(end_val)}{suffix}")
            return
            
        anim = QVariantAnimation(label)
        anim.setDuration(duration)
        anim.setStartValue(float(start_val))
        anim.setEndValue(float(end_val))
        anim.setEasingCurve(QEasingCurve.OutExpo)
        
        def update_text(val):
            if is_float:
                label.setText(f"{prefix}{val:,.2f}{suffix}")
            else:
                label.setText(f"{prefix}{int(val)}{suffix}")
                
        anim.valueChanged.connect(update_text)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        label._count_anim = anim

    @staticmethod
    def slide_in(widget, start_pos, end_pos, duration=500):
        if not Animations._is_enabled():
            widget.move(end_pos)
            return
            
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(start_pos)
        anim.setEndValue(end_pos)
        anim.setEasingCurve(QEasingCurve.OutExpo)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        widget._slide_anim = anim

    @staticmethod
    def fly_to_cart(parent_widget, start_pos, end_pos, text):
        if not Animations._is_enabled():
            return
            
        fly_widget = QFrame(parent_widget)
        fly_widget.setFixedSize(140, 45)
        fly_widget.move(start_pos)
        fly_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        fly_widget.setStyleSheet("background-color: #6366F1; border-radius: 22px; border: 1px solid #818CF8;")
        Animations.apply_glow(fly_widget, "#6366F1", 20, 100)
        
        layout = QVBoxLayout(fly_widget)
        layout.setContentsMargins(0,0,0,0)
        lbl = QLabel(text)
        lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent; border: none;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        fly_widget.show()
        fly_widget.raise_()
        
        anim_pos = QPropertyAnimation(fly_widget, b"pos")
        anim_pos.setDuration(700)
        anim_pos.setStartValue(start_pos)
        anim_pos.setEndValue(end_pos)
        anim_pos.setEasingCurve(QEasingCurve.InOutBack)
        
        effect = QGraphicsOpacityEffect(fly_widget)
        fly_widget.setGraphicsEffect(effect)
        anim_op = QPropertyAnimation(effect, b"opacity")
        anim_op.setDuration(700)
        anim_op.setStartValue(1.0)
        anim_op.setEndValue(0.0)
        anim_op.setEasingCurve(QEasingCurve.InExpo)
        
        anim_scale = QPropertyAnimation(fly_widget, b"geometry")
        anim_scale.setDuration(700)
        anim_scale.setStartValue(QRectF(start_pos.x(), start_pos.y(), 140, 45))
        anim_scale.setEndValue(QRectF(end_pos.x(), end_pos.y(), 40, 15))
        
        group = QParallelAnimationGroup(parent_widget)
        group.addAnimation(anim_pos)
        group.addAnimation(anim_op)
        group.addAnimation(anim_scale)
        group.finished.connect(fly_widget.deleteLater)
        group.start(QPropertyAnimation.DeleteWhenStopped)
        fly_widget._group = group

    @staticmethod
    def shake(widget):
        if not Animations._is_enabled():
            return
            
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(500)
        pos = widget.pos()
        anim.setKeyValueAt(0.0, pos)
        anim.setKeyValueAt(0.1, pos + QPoint(-15, 0))
        anim.setKeyValueAt(0.3, pos + QPoint(15, 0))
        anim.setKeyValueAt(0.5, pos + QPoint(-15, 0))
        anim.setKeyValueAt(0.7, pos + QPoint(15, 0))
        anim.setKeyValueAt(0.9, pos + QPoint(-15, 0))
        anim.setKeyValueAt(1.0, pos)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        widget._shake_anim = anim

class Toast(QWidget):
    def __init__(self, parent, message, color="#10B981"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        frame = QFrame()
        frame.setStyleSheet(f"background-color: rgba(24, 24, 27, 0.95); border: 1px solid {color}; border-radius: 14px;")
        Animations.apply_glow(frame, color, 40, 70)
        
        h_layout = QHBoxLayout(frame)
        h_layout.setContentsMargins(25, 20, 25, 20)
        
        lbl = QLabel(message)
        lbl.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 16px; border: none; background: transparent; letter-spacing: 0.5px;")
        h_layout.addWidget(lbl)
        
        layout.addWidget(frame)
        
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"QProgressBar {{ border: none; background: transparent; }} QProgressBar::chunk {{ background-color: {color}; border-radius: 2px; }}")
        self.progress.setValue(100)
        layout.addWidget(self.progress)
        
        self.adjustSize()

    def show_toast(self, x, y):
        self.move(x, y + 60)
        self.show()
        
        if not Animations._is_enabled():
            self.move(x, y)
            QTimer.singleShot(4000, self.close)
            return
            
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        
        self.anim_group = QParallelAnimationGroup()
        
        op_anim = QPropertyAnimation(self.effect, b"opacity")
        op_anim.setDuration(500)
        op_anim.setStartValue(0.0)
        op_anim.setEndValue(1.0)
        op_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        pos_anim = QPropertyAnimation(self, b"pos")
        pos_anim.setDuration(700)
        pos_anim.setStartValue(QPoint(x, y + 60))
        pos_anim.setEndValue(QPoint(x, y))
        pos_anim.setEasingCurve(QEasingCurve.OutBack)
        
        self.anim_group.addAnimation(op_anim)
        self.anim_group.addAnimation(pos_anim)
        self.anim_group.start()
        
        self.prog_anim = QPropertyAnimation(self.progress, b"value")
        self.prog_anim.setDuration(4000)
        self.prog_anim.setStartValue(100)
        self.prog_anim.setEndValue(0)
        self.prog_anim.start()
        
        QTimer.singleShot(4000, self.hide_toast)

    def hide_toast(self):
        if not Animations._is_enabled():
            self.close()
            return
            
        op_anim = QPropertyAnimation(self.effect, b"opacity")
        op_anim.setDuration(500)
        op_anim.setStartValue(1.0)
        op_anim.setEndValue(0.0)
        op_anim.finished.connect(self.close)
        op_anim.start()
        self._hide_anim = op_anim

class ToastManager:
    @staticmethod
    def show_success(parent, message):
        t = Toast(parent, "✔️  " + message, "#10B981")
        x = parent.width() // 2 - t.width() // 2
        y = parent.height() - 150
        t.show_toast(x, y)

    @staticmethod
    def show_error(parent, message):
        t = Toast(parent, "⚠️  " + message, "#EF4444")
        x = parent.width() // 2 - t.width() // 2
        y = parent.height() - 150
        t.show_toast(x, y)

    @staticmethod
    def show_warning(parent, message):
        t = Toast(parent, "⚠️  " + message, "#F59E0B")
        x = parent.width() // 2 - t.width() // 2
        y = parent.height() - 150
        t.show_toast(x, y)

    @staticmethod
    def show_info(parent, message):
        t = Toast(parent, "ℹ️  " + message, "#6366F1")
        x = parent.width() // 2 - t.width() // 2
        y = parent.height() - 150
        t.show_toast(x, y)

class ParticleBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.particles = []
        if not Animations._is_enabled(): return
        
        import random
        for _ in range(60):
            self.particles.append({
                'x': random.uniform(0, 2000),
                'y': random.uniform(0, 1200),
                'vx': random.uniform(-0.4, 0.4),
                'vy': random.uniform(-0.4, 0.4),
                'size': random.uniform(2, 6),
                'alpha': random.uniform(20, 90)
            })
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16) # Smooth 60fps

    def update_particles(self):
        w, h = self.width(), self.height()
        if w == 0 or h == 0: return
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['x'] < 0: p['x'] = w
            if p['x'] > w: p['x'] = 0
            if p['y'] < 0: p['y'] = h
            if p['y'] > h: p['y'] = 0
        self.update()

    def paintEvent(self, event):
        if not Animations._is_enabled(): return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for p in self.particles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(99, 102, 241, int(p['alpha'])))
            painter.drawEllipse(QRectF(p['x'], p['y'], p['size'], p['size']))
