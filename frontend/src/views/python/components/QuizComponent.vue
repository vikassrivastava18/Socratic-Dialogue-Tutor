<template>
	<div class="container my-4">
		<h3 class="mb-4">Quiz</h3>

		<p v-if="isLoading">Loading quizzes...</p>
		<p v-else-if="errorMessage" class="text-danger">{{ errorMessage }}</p>
		<p v-else-if="!hasQuizzes">No quizzes are available for this subtopic.</p>

		<form v-else @submit.prevent="submitQuiz">
			<section v-for="section in quizSections" :key="section.key" class="mb-4">
				<h4>{{ section.title }}</h4>				
				<div
					v-for="(quiz, index) in section.items"
					:key="quiz.id ?? `${section.key}-${index}`"
					class="card mb-3 p-3"
				>
					<p><strong>{{ index + 1 }}. {{ quiz.question }}</strong></p>
                    
					<template v-if="section.key === 'mcq'">
						<div v-for="option in quiz.options" :key="option" class="form-check">
							<input
								:id="`${section.key}-${index}-${option}`"
								v-model="responses[section.key][index]"
								class="form-check-input"
								type="radio"
								:name="`${section.key}-${index}`"
								:value="option"
							/>
							<label class="form-check-label" :for="`${section.key}-${index}-${option}`">
								{{ option }}
							</label>
						</div>
					</template>

					<template v-else-if="section.key === 'true_false'">
						<div v-for="option in [true, false]" :key="String(option)" class="form-check">
							<input
								:id="`${section.key}-${index}-${option}`"
								v-model="responses[section.key][index]"
								class="form-check-input"
								type="radio"
								:name="`${section.key}-${index}`"
								:value="option"
							/>
							<label class="form-check-label" :for="`${section.key}-${index}-${option}`">
								{{ option ? 'True' : 'False' }}
							</label>
						</div>
					</template>

					<input
						v-else
						v-model="responses[section.key][index]"
						class="form-control"
						type="text"
						placeholder="Enter answer"
					/>
				</div>
			</section>

			<button class="btn btn-primary" type="submit" :disabled="isSubmitting">
				{{ isSubmitting ? 'Submitting...' : 'Submit Answers' }}
			</button>
		</form>

		<div v-if="evaluation" class="alert alert-info mt-4" role="status">
			Submitted, your score: {{ evaluationMessage }}
			
		</div>
	</div>

	<!-- Modal -->
    <div class="modal fade" id="exampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content rounded-4 shadow">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">Take hints to complete and proceed</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>

          <div class="modal-body">
            
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button type="button" class="btn btn-primary" @click="borrowBook">
              Agree
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { baseUrl } from "../../../config";

const route = useRoute();
const quizzes = ref({});
const isLoading = ref(true);
const isSubmitting = ref(false);
const errorMessage = ref("");
const evaluation = ref(null);
const responses = reactive({ mcq: [], true_false: []});

const quizSections = computed(() => [
	{ key: "mcq", title: "Multiple Choice", items: quizzes.value.mcq || [] },
	{ key: "true_false", title: "True / False", items: quizzes.value.true_false || [] },
]);

const hasQuizzes = computed(() => quizSections.value.some((section) => section.items.length));

const evaluationMessage = computed(() => {
	if (typeof evaluation.value === "string") return evaluation.value;
	return evaluation.value?.message || evaluation.value?.score + '/' + evaluation.value?.total || "Your answers were submitted.";
});

function normalizeQuizResponse(data) {
	if (Array.isArray(data)) return { mcq: data };
	return data.quizzes || data;
}

async function loadQuizzes() {
	try {
		const response = await fetch(`${baseUrl}/subtopics/${route.params.id}/quizzes`);
		if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
		quizzes.value = normalizeQuizResponse(await response.json());
	} catch (error) {
		errorMessage.value = "Unable to load quizzes. Please try again.";
		console.error("Failed to load quizzes:", error);
	} finally {
		isLoading.value = false;
	}
}

async function submitQuiz() {
	isSubmitting.value = true;
	errorMessage.value = "";
	evaluation.value = null;

	try {
		const response = await fetch(`${baseUrl}/subtopics/${route.params.id}/quizzes/evaluate/`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ answers: { ...responses } }),
		});
		if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
				
		evaluation.value = await response.json();
		console.log("Response: ", evaluation.value);
	} catch (error) {
		errorMessage.value = "Unable to submit your answers. Please try again.";
		console.error("Failed to evaluate quiz:", error);
	} finally {
		isSubmitting.value = false;
	}
}

onMounted(loadQuizzes);
</script>

<style scoped>
h3 {
    color: maroon;
}
</style>
