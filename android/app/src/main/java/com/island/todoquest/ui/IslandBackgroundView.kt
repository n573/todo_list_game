package com.island.todoquest.ui

import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import androidx.core.content.ContextCompat
import com.island.todoquest.R

class IslandBackgroundView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val width = width.toFloat()
        val height = height.toFloat()

        val skyTop = ContextCompat.getColor(context, R.color.sky_top)
        val skyBottom = ContextCompat.getColor(context, R.color.sky_bottom)
        val seaDark = ContextCompat.getColor(context, R.color.sea_dark)
        val seaLight = ContextCompat.getColor(context, R.color.sea_light)
        val islandSand = ContextCompat.getColor(context, R.color.island_sand)
        val islandGrass = ContextCompat.getColor(context, R.color.island_grass)

        val skyHeight = height * 0.35f
        paint.color = skyTop
        canvas.drawRect(0f, 0f, width, skyHeight, paint)
        paint.color = skyBottom
        canvas.drawRect(0f, skyHeight, width, skyHeight + 20f, paint)

        var y = skyHeight + 20f
        val bandHeight = 18f
        var toggle = true
        while (y < height) {
            paint.color = if (toggle) seaLight else seaDark
            canvas.drawRect(0f, y, width, minOf(y + bandHeight, height), paint)
            toggle = !toggle
            y += bandHeight
        }

        val islandWidth = width * 0.45f
        val islandHeight = height * 0.22f
        val islandX0 = width * 0.28f
        val islandY0 = height * 0.48f
        paint.color = islandSand
        canvas.drawOval(islandX0, islandY0, islandX0 + islandWidth, islandY0 + islandHeight, paint)
        paint.color = islandGrass
        canvas.drawOval(
            islandX0 + 30f,
            islandY0 + 12f,
            islandX0 + islandWidth - 30f,
            islandY0 + islandHeight - 18f,
            paint
        )

        paint.color = ContextCompat.getColor(context, R.color.palm_trunk)
        val palmX = islandX0 + islandWidth * 0.2f
        val palmY = islandY0 + islandHeight * 0.15f
        canvas.drawRect(palmX, palmY, palmX + 6f, palmY + 40f, paint)
        paint.color = ContextCompat.getColor(context, R.color.palm_leaf)
        canvas.drawRect(palmX - 14f, palmY - 6f, palmX + 20f, palmY + 4f, paint)
    }
}
