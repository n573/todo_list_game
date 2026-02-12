package com.island.todoquest.ui

import android.animation.ObjectAnimator
import android.animation.AnimatorSet
import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import android.view.animation.OvershootInterpolator
import androidx.core.content.ContextCompat
import com.island.todoquest.R
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.PI

class LevelUpOverlayView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var level: Int = 1
    private var scaleLevel = 1f
    private var starsScale = 1f
    private var alphaOverlay = 0.5f

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = 80f
        textAlign = Paint.Align.CENTER
    }
    private val shadowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        textSize = 80f
        textAlign = Paint.Align.CENTER
    }

    fun show(newLevel: Int, onComplete: () -> Unit) {
        level = newLevel
        scaleLevel = 1f
        starsScale = 1f
        alphaOverlay = 0.5f

        textPaint.color = ContextCompat.getColor(context, R.color.accent)
        shadowPaint.color = ContextCompat.getColor(context, R.color.panel)
        shadowPaint.alpha = 200

        // Animate scale
        val scaleAnimator = ObjectAnimator.ofFloat(this, "scaleLevel", 1f, 1.3f, 1.1f, 1.25f, 1.15f).apply {
            duration = 1500
            interpolator = OvershootInterpolator(1.5f)
        }

        // Animate stars
        val starsAnimator = ObjectAnimator.ofFloat(this, "starsScale", 1f, 1.5f, 1.3f).apply {
            duration = 1200
        }

        // Animate overlay fade
        val fadeAnimator = ObjectAnimator.ofFloat(this, "alphaOverlay", 0.5f, 0.3f).apply {
            duration = 1500
        }

        val set = AnimatorSet().apply {
            playTogether(scaleAnimator, starsAnimator, fadeAnimator)
            addListener(object : android.animation.Animator.AnimatorListener {
                override fun onAnimationStart(animation: android.animation.Animator) {}
                override fun onAnimationEnd(animation: android.animation.Animator) {
                    onComplete()
                }
                override fun onAnimationCancel(animation: android.animation.Animator) {}
                override fun onAnimationRepeat(animation: android.animation.Animator) {}
            })
        }
        set.start()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val centerX = width / 2f
        val centerY = height / 2f

        // Semi-transparent overlay
        paint.color = ContextCompat.getColor(context, R.color.panel)
        paint.alpha = (alphaOverlay * 255).toInt()
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)

        // Draw stars
        val starRadius = 100f
        val numStars = 6
        for (i in 0 until numStars) {
            val angle = (i / numStars.toFloat()) * 2 * PI.toFloat()
            val starX = centerX + (starRadius * starsScale) * cos(angle)
            val starY = centerY + (starRadius * starsScale) * sin(angle)
            paint.color = ContextCompat.getColor(context, R.color.accent)
            paint.textSize = 48f * starsScale
            canvas.drawText("★", starX, starY, paint)
        }

        // Draw level-up text with shadow and scale
        val boxPadding = 60f * scaleLevel
        val boxLeft = centerX - boxPadding
        val boxTop = centerY - 60f * scaleLevel
        val boxRight = centerX + boxPadding
        val boxBottom = centerY + 60f * scaleLevel

        // Shadow effect
        shadowPaint.textSize = 80f * scaleLevel
        canvas.drawText("LEVEL $level!", centerX + 4f, centerY + 30f * scaleLevel + 4f, shadowPaint)

        // Main text
        textPaint.textSize = 80f * scaleLevel
        canvas.drawText("LEVEL $level!", centerX, centerY + 30f * scaleLevel, textPaint)
    }

    // Property setters for animation
    fun setScaleLevel(value: Float) {
        scaleLevel = value
        invalidate()
    }

    fun setStarsScale(value: Float) {
        starsScale = value
        invalidate()
    }

    fun setAlphaOverlay(value: Float) {
        alphaOverlay = value
        invalidate()
    }
}
