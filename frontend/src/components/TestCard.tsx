export default function TestCard() {
  return (
    <div className="max-w-sm mx-auto mt-10 p-6 border rounded-lg bg-background text-foreground shadow-sm">
      <h2 className="text-xl font-bold mb-3">Tailwind Theme Test</h2>
      <p className="text-muted-foreground mb-4">
        If you can read this with correct colors, your Tailwind theme is working 🎉
      </p>
      <button className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/80">
        Test Button
      </button>
    </div>
  );
}
