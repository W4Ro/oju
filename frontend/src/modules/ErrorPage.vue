<template>
  <div class="error-page">
    <svg xmlns="http://www.w3.org/2000/svg" id="robot-error" viewBox="0 0 260 118.9" role="img">
      <title xml:lang="en">404 Error</title>

      <defs>
        <clipPath id="white-clip">
          <circle id="white-eye" fill="#cacaca" cx="130" cy="65" r="20" />
        </clipPath>
        <text id="text-s" class="error-text" y="106">404</text>
      </defs>

      <path class="alarm" fill="#e62326" d="M120.9 19.6V9.1c0-5 4.1-9.1 9.1-9.1h0c5 0 9.1 4.1 9.1 9.1v10.6" />
      <use xlink:href="#text-s" x="-0.5px" y="-1px" fill="black"></use>
      <use xlink:href="#text-s" fill="#2b2b2b"></use>

      <g id="robot">
        <g id="eye-wrap">
          <use xlink:href="#white-eye"></use>
          <circle
            id="eyef"
            class="eye"
            :cx="eyePosition.x"
            :cy="eyePosition.y"
            clip-path="url(#white-clip)"
            fill="#000"
            stroke="#2aa7cc"
            stroke-width="2"
            stroke-miterlimit="10"
            r="11"
          />
          <ellipse fill="#2b2b2b" cx="130" cy="40" rx="18" ry="12" />
        </g>

        <circle class="lightblue" cx="105" cy="32" r="2.5" id="tornillo" />
        <use xlink:href="#tornillo" x="50"></use>
        <use xlink:href="#tornillo" x="50" y="60"></use>
        <use xlink:href="#tornillo" y="60"></use>
      </g>
    </svg>

    <h1>Oops! Page Not Found</h1>
    <h2>We couldn't find the page you were looking for</h2>
    <h3>Go back to <a href="/dashboard">Dashboard</a></h3>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const eyePosition = ref({ x: 130, y: 65 });

const handleMove = (event: MouseEvent | TouchEvent) => {
  let clientX, clientY;

  if (event instanceof MouseEvent) {
    clientX = event.clientX;
    clientY = event.clientY;
  } else {
    clientX = event.touches[0].clientX;
    clientY = event.touches[0].clientY;
  }

  const x = clientX / window.innerWidth;
  const y = clientY / window.innerHeight;

  eyePosition.value.x = 115 + 30 * x;
  eyePosition.value.y = 50 + 30 * y;
};

onMounted(() => {
  document.addEventListener('mousemove', handleMove);
  document.addEventListener('touchmove', handleMove);
});

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMove);
  document.removeEventListener('touchmove', handleMove);
});
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}
</style>

<style scoped>
@import url("https://fonts.googleapis.com/css?family=Bungee");

.error-page {
  background: #1b1b1b;
  color: white;
  font-family: "Bungee", cursive;
  text-align: center;
 
  min-height: 100vh;
  width: 100%;
  padding: 2rem 1rem;
 
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

a {
  color: #2aa7cc;
  text-decoration: none;
  transition: color 0.3s ease;
}

a:hover {
  color: #4ecdf5;
}

svg {
  width: min(50vw, 300px);
  height: auto;
  margin-bottom: 2rem;
}

.lightblue {
  fill: #444;
}

.error-text {
  font-size: min(120px, 20vw);
}

h1 {
  font-size: min(2.5rem, 7vw);
  margin: 1rem 5%;
  color: #ff6b6b;
}

h2 {
  font-size: min(1.8rem, 5vw);
  margin: 0.5rem 10%;
  font-weight: normal;
}

h3 {
  font-size: min(1.5rem, 4vw);
  margin-top: 2rem;
}

.alarm {
  animation: alarmOn 0.5s infinite;
}

#eye-wrap {
  overflow: hidden;
}

@keyframes alarmOn {
  to {
    fill: darkred;
  }
}

#robot {
  animation: shake 2s ease-in-out infinite;
  transform-origin: center;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-2px) rotate(-1deg);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(2px) rotate(1deg);
  }
}
</style>