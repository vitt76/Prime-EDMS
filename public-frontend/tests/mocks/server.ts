/**
 * MSW Server Setup
 * 
 * Creates the mock server for Node.js (testing) environment
 */
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
