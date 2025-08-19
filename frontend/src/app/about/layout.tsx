export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <nav style={{ padding: "10px", background: "#eee" }}>
          <a href="/">Home</a> | <a href="/about">About</a>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  )
}
