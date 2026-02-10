<template>
  <div class="min-h-screen bg-white text-neutral-900 dark:bg-neutral-950 dark:text-neutral-50">
    <Navigation />
    <main class="min-h-[70vh]">
      <slot />
    </main>
    <Footer />
  </div>
</template>
