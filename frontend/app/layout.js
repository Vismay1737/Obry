import './globals.css'

export const metadata = {
  title: 'OrbyTech - AI Cybersecurity Copilot',
  description: 'AI-powered vulnerability analysis system',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
