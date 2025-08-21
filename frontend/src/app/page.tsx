// src/app/page.tsx
export default function HomePage() {
  return (
    <div className="bg-background text-foreground flex flex-1 flex-col items-center justify-center p-8">
      <h1 className="mb-4 text-4xl font-bold">Welcome to OWASP Nest</h1>
      <p className="text-muted-foreground text-lg">
        This is the Home Page built with Next.js 15 (App Router).
      </p>
    </div>
  )
}
