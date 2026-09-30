import "./globals.css";

export const metadata = {
  title: "SolveSpheare | Product Intelligence",
  description: "Product Review Intelligence and Voice of Customer Analytics"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
