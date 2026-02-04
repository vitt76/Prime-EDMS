import { defineStore } from 'pinia'

export const useContentStore = defineStore('content', {
  state: () => ({
    pages: new Map<string, any>(),
    posts: new Map<string, any>()
  }),
  actions: {
    cachePage(slug: string, data: any) {
      this.pages.set(slug, data)
    },
    cachePost(slug: string, data: any) {
      this.posts.set(slug, data)
    }
  }
})
