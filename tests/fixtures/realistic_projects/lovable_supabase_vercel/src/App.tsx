import { supabase } from './lib/supabase'
import { ClerkProvider } from './lib/auth'

export default function App() {
  return (
    <ClerkProvider>
      <div>My App</div>
    </ClerkProvider>
  )
}
