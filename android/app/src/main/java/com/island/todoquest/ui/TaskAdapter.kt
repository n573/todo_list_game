package com.island.todoquest.ui

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import androidx.recyclerview.widget.RecyclerView
import com.island.todoquest.R
import com.island.todoquest.data.Task

class TaskAdapter(
    private val tasks: MutableList<Task>,
    private val onComplete: (Task) -> Unit,
    private val onDelete: (Task) -> Unit,
    private val onTextChanged: (Task, String) -> Unit,
    private val onWeightChanged: (Task, Int) -> Unit
) : RecyclerView.Adapter<TaskAdapter.TaskViewHolder>() {

    private val weightOptions = listOf("1", "2", "3", "4", "5")

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TaskViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_task, parent, false)
        return TaskViewHolder(view, weightOptions, onComplete, onDelete, onTextChanged, onWeightChanged)
    }

    override fun onBindViewHolder(holder: TaskViewHolder, position: Int) {
        holder.bind(tasks[position])
    }

    override fun getItemCount(): Int = tasks.size

    fun replaceItems(newItems: List<Task>) {
        val copy = newItems.toList()
        tasks.clear()
        tasks.addAll(copy)
        notifyDataSetChanged()
    }

    class TaskViewHolder(
        itemView: View,
        weightOptions: List<String>,
        private val onComplete: (Task) -> Unit,
        private val onDelete: (Task) -> Unit,
        private val onTextChanged: (Task, String) -> Unit,
        private val onWeightChanged: (Task, Int) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {

        private val taskEdit: EditText = itemView.findViewById(R.id.task_edit)
        private val weightSpinner: Spinner = itemView.findViewById(R.id.task_weight_spinner)
        private val doneButton: Button = itemView.findViewById(R.id.task_done)
        private val deleteButton: Button = itemView.findViewById(R.id.task_delete)

        private var boundTask: Task? = null
        private var suppressCallbacks = false

        init {
            val adapter = ArrayAdapter(itemView.context, R.layout.spinner_item, weightOptions)
            adapter.setDropDownViewResource(R.layout.spinner_dropdown_item)
            weightSpinner.adapter = adapter

            weightSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    parent: AdapterView<*>?,
                    view: View?,
                    position: Int,
                    id: Long
                ) {
                    if (suppressCallbacks) return
                    val task = boundTask ?: return
                    val weight = position + 1
                    if (task.weight != weight) {
                        onWeightChanged(task, weight)
                    }
                }

                override fun onNothingSelected(parent: AdapterView<*>?) {
                    return
                }
            }

            taskEdit.setOnFocusChangeListener { _, hasFocus ->
                if (hasFocus) return@setOnFocusChangeListener
                val task = boundTask ?: return@setOnFocusChangeListener
                val updatedText = taskEdit.text.toString().trim()
                if (updatedText != task.text) {
                    onTextChanged(task, updatedText)
                }
            }

            doneButton.setOnClickListener {
                boundTask?.let(onComplete)
            }

            deleteButton.setOnClickListener {
                boundTask?.let(onDelete)
            }
        }

        fun bind(task: Task) {
            boundTask = task
            suppressCallbacks = true
            taskEdit.setText(task.text)
            weightSpinner.setSelection(task.weight - 1, false)
            suppressCallbacks = false
        }
    }
}
