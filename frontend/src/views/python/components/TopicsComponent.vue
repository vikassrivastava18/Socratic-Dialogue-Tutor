<template>
    <div class="container my-2 p-2">
        
        <div v-for="topic in topics" :key="topic.id">
            <div class="card" style="width: 18rem;">
                <router-link class="topic-link" :to="`/python/topic-summary/${topic.id}`">

                    <img src="../../../assets/regex.jpg" class="card-img-top" alt="...">
                    <div class="card-body">
                        <p class="card-text">{{ topic.title }}</p>
                    </div>
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { baseUrl } from "../../../config";

const topics = ref([]);

onMounted(async () => {
    try {
        const response = await fetch(`${baseUrl}/topics/`);

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        topics.value = await response.json();
    } catch (error) {
        console.error("Failed to load topics:", error);
    }
});
</script>

<style scoped>
.theory-container {
    padding: 24px;
}

h3 {
    margin: 0 0 16px;
    /* font-size: 1.5rem; */
    color: maroon;
    /* text-align: center; */
}

.theory-iframe {
    width: 100%;
    min-height: 800px;
    border: 1px solid #dfe3e8;
    border-radius: 10px;
    background: #fff;
}

.topic-link {
    font-size: 1.25rem;
}
</style>