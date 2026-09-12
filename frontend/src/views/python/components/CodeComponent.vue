<template>
  <div class="container">
    <div class="row g-4 coding-layout">
      <!-- Left column: question -->
      <div class="col-md-5">
        <div class="card h-100">
          <div class="card-header">
            Question
          </div>
          <div class="card-body">
            <p>{{ question || "Loading question..." }}</p>
          </div>
        </div>
      </div>

      <!-- Right column -->
      <div class="col-md-7 coding-column">
        <!-- Code row -->
        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            Write Your Code
            <router-link
              v-if="answerMatches && !hasNextProblem && nextTopicId"
              class="btn btn-success btn-sm"
              :to="`/python/subtopic/${nextTopicId}/summary`"
            >
              Next topic
            </router-link>
          </div>
          <div class="card-body">
            <textarea
              v-model="code"
              id="codeArea"
              class="form-control"
              rows="10"
              @paste.prevent
              spellcheck="false"
              @keydown.tab.prevent="insertIndentation"
            ></textarea>

            <div class="d-flex align-items-end mt-3 gap-3">
              <button
                class="btn btn-primary"
                @click="executeCode"
                :disabled="loading"
              >
                {{ loading ? "Loading..." : "Run Python" }}
              </button>

              <div
                v-if="output"
                class="alert mb-0 p-2 "
                :class="answerMatches ? 'alert-success' : 'alert-danger'"
              >
                {{ answerMatches ? "Correct answer" : "Answers do not match" }}
              </div>

              <button
                v-if="answerMatches && hasNextProblem"
                class="btn btn-success"
                @click="loadNextProblem"
              >
                Next problem
              </button>
            </div>

            <h5 class="mt-4">Your Output</h5>
            <pre class="bg-light p-3">{{ output }}</pre>
          </div>
        </div>

        <!-- Expected answer row -->
        <div class="card">
          <div class="card-header">
            Match Answer
          </div>
          <div class="card-body">
            <label for="expectedAnswer" class="form-label">
              Expected answer
            </label>

            <textarea
              id="expectedAnswer"
              v-model="expectedAnswer"
              class="form-control"
              rows="4"              
            ></textarea>
            
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { runPython, initializePython } from "../../../services/pythonRunner";
import { baseUrl } from "../../../config";

const route = useRoute();
const question = ref("");
const code = ref("");
const output = ref("");
const expectedAnswer = ref("");
const loading = ref(true);
const codingProblems = ref([]);
const currentProblemIndex = ref(0);
const nextTopicId = ref(null);

const hasNextProblem = computed(
  () => currentProblemIndex.value < codingProblems.value.length - 1
);

function loadProblem(problem) {
  question.value = problem.problem;
  code.value = problem.code;
  expectedAnswer.value = String(problem.answer);
  output.value = "";
}

onMounted(async () => {
  try {
    await initializePython()
    const response = await fetch(
      `${baseUrl}/subtopics/${route.params.id}/coding-problems/`
    );

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    codingProblems.value = data.codes.codes || [];
    nextTopicId.value = data.next_id;
    const problem = codingProblems.value[0];

    if (!problem) {
      throw new Error("No coding problems were returned");
    }

    loadProblem(problem);
  } catch (error) {
    console.error("Failed to load code snippet:", error);
  } finally {
    loading.value = false
  }

});

function loadNextProblem() {
  if (!hasNextProblem.value) {
    return;
  }

  currentProblemIndex.value += 1;
  loadProblem(codingProblems.value[currentProblemIndex.value]);
}

async function executeCode() {
  loading.value = true;
  output.value = "";

  try {
    const result = await runPython(code.value);
    output.value = String(result ?? "");
  } catch (error) {
    output.value = String(error);
  } finally {
    loading.value = false;
  }
}

const answerMatches = computed(() =>
  output.value.trim() === expectedAnswer.value.trim()
);

function insertIndentation(event) {
  const textarea = event.target;
  const indentation = "    ";
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;

  code.value =
    code.value.substring(0, start) +
    indentation +
    code.value.substring(end);

  requestAnimationFrame(() => {
    textarea.selectionStart = textarea.selectionEnd =
      start + indentation.length;
  });
}
</script>

<style>
#codeArea {
  border: 1px dotted;
}
</style>
