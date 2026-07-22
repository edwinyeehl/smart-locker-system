import "./globals.css";

export const metadata = {
  title: "Smart Locker Simulator | Admin & User Dashboard",
  description: "Sleek glassmorphic interface for simulating smart locker stations, courier deposits, and recipient collections.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
