package com.island.todoquest

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.inputmethod.EditorInfo
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.island.todoquest.data.Task
import com.island.todoquest.data.TaskRepository
import com.island.todoquest.data.TodoState
import com.island.todoquest.ui.HistoryAdapter
import com.island.todoquest.ui.LevelUpOverlayView
import com.island.todoquest.ui.TaskAdapter
import java.util.UUID

class MainActivity : AppCompatActivity() {

    private lateinit var repository: TaskRepository
    private lateinit var state: TodoState

    private lateinit var levelLabel: TextView
    private lateinit var xpLabel: TextView
    private lateinit var xpBar: ProgressBar
    private lateinit var emptyTasksLabel: TextView
    private lateinit var newTaskEdit: EditText
    private lateinit var newWeightSpinner: Spinner
    private lateinit var addButton: Button
    private lateinit var levelUpOverlay: LevelUpOverlayView
    private lateinit var taskAdapter: TaskAdapter
    private lateinit var historyAdapter: HistoryAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        repository = TaskRepository(this)
        state = repository.load()

        levelLabel = findViewById(R.id.level_label)
        xpLabel = findViewById(R.id.xp_label)
        xpBar = findViewById(R.id.xp_bar)
        emptyTasksLabel = findViewById(R.id.empty_tasks)
        newTaskEdit = findViewById(R.id.new_task_edit)
        newWeightSpinner = findViewById(R.id.new_weight_spinner)
        addButton = findViewById(R.id.add_task_button)
        levelUpOverlay = findViewById(R.id.level_up_overlay)

        val weightOptions = listOf("1", "2", "3", "4", "5")
        val spinnerAdapter = ArrayAdapter(this, R.layout.spinner_item, weightOptions)
        spinnerAdapter.setDropDownViewResource(R.layout.spinner_dropdown_item)
        newWeightSpinner.adapter = spinnerAdapter
        newWeightSpinner.setSelection(1)

        taskAdapter = TaskAdapter(
            state.tasks,
            onComplete = { completeTask(it) },
            onDelete = { deleteTask(it) },
            onWeightChanged = { task, weight -> updateTaskWeight(task, weight) }
        )

        val taskList = findViewById<RecyclerView>(R.id.task_list)
        taskList.layoutManager = LinearLayoutManager(this)
        taskList.adapter = taskAdapter
        taskList.isNestedScrollingEnabled = false

        historyAdapter = HistoryAdapter(state.history)
        val historyList = findViewById<RecyclerView>(R.id.history_list)
        historyList.layoutManager = LinearLayoutManager(this)
        historyList.adapter = historyAdapter
        historyList.isNestedScrollingEnabled = false

        addButton.setOnClickListener { addTask() }
        newTaskEdit.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                addTask()
                true
            } else {
                false
            }
        }

        refreshUI()
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.menu_clear_history -> {
                showClearHistoryDialog()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun showClearHistoryDialog() {
        AlertDialog.Builder(this)
            .setTitle("Clear History")
            .setMessage("Are you sure you want to clear all completed quests?")
            .setPositiveButton("Clear") { _: android.content.DialogInterface, _: Int ->
                state.history.clear()
                refreshUI()
                persist()
                Toast.makeText(this, "History cleared", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun addTask() {
        val text = newTaskEdit.text.toString().trim()
        if (text.isEmpty()) return

        val weight = safeWeight(newWeightSpinner.selectedItem?.toString())
        val task = Task(
            id = UUID.randomUUID().toString().replace("-", ""),
            text = text,
            weight = weight
        )
        state.tasks.add(task)
        newTaskEdit.text.clear()
        newWeightSpinner.setSelection(1)
        refreshUI()
        persist()
    }

    private fun completeTask(task: Task) {
        val oldLevel = levelForXp(state.xp)
        state.tasks.remove(task)
        task.completed = true
        task.completedAt = "now"
        state.history.add(0, task)
        state.xp += task.weight * XP_PER_WEIGHT
        trimHistory()

        refreshUI()
        persist()

        val newLevel = levelForXp(state.xp)
        if (newLevel > oldLevel) {
            levelUpOverlay.bringToFront()
            levelUpOverlay.visibility = android.view.View.VISIBLE
            levelUpOverlay.show(newLevel) {
                levelUpOverlay.visibility = android.view.View.GONE
            }
        }
    }

    private fun deleteTask(task: Task) {
        state.tasks.remove(task)
        refreshUI()
        persist()
    }

    private fun updateTaskWeight(task: Task, weight: Int) {
        task.weight = weight
        persist()
    }

    private fun refreshUI() {
        taskAdapter.replaceItems(state.tasks)
        historyAdapter.replaceItems(state.history)
        emptyTasksLabel.visibility = if (state.tasks.isEmpty()) android.view.View.VISIBLE else android.view.View.GONE
        updateXpDisplay()
    }

    private fun updateXpDisplay() {
        val level = levelForXp(state.xp)
        val xpIntoLevel = state.xp % XP_PER_LEVEL
        levelLabel.text = "Level $level"
        xpLabel.text = "XP: $xpIntoLevel / $XP_PER_LEVEL"
        xpBar.max = XP_PER_LEVEL
        xpBar.progress = xpIntoLevel
    }

    private fun trimHistory() {
        if (state.history.size <= HISTORY_LIMIT) return
        while (state.history.size > HISTORY_LIMIT) {
            state.history.removeAt(state.history.size - 1)
        }
    }

    private fun persist() {
        repository.save(state)
    }

    private fun safeWeight(value: String?): Int {
        val parsed = value?.toIntOrNull() ?: 1
        return parsed.coerceIn(1, 5)
    }

    private fun levelForXp(xp: Int): Int {
        return xp / XP_PER_LEVEL + 1
    }

    companion object {
        private const val XP_PER_WEIGHT = 10
        private const val XP_PER_LEVEL = 100
        private const val HISTORY_LIMIT = 200
    }
}
