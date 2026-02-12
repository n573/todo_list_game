package com.island.todoquest.ui

import android.graphics.Paint
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.island.todoquest.R
import com.island.todoquest.data.Task

class HistoryAdapter(
    private val history: MutableList<Task>
) : RecyclerView.Adapter<HistoryAdapter.HistoryViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): HistoryViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_history, parent, false)
        return HistoryViewHolder(view)
    }

    override fun onBindViewHolder(holder: HistoryViewHolder, position: Int) {
        holder.bind(history[position])
    }

    override fun getItemCount(): Int = history.size

    fun replaceItems(newItems: List<Task>) {
        val copy = newItems.toList()
        history.clear()
        history.addAll(copy)
        notifyDataSetChanged()
    }

    class HistoryViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val historyText: TextView = itemView.findViewById(R.id.history_text)

        fun bind(task: Task) {
            val label = "[x] ${task.text} (W:${task.weight})"
            historyText.text = label
            historyText.paintFlags = historyText.paintFlags or Paint.STRIKE_THRU_TEXT_FLAG
        }
    }
}
