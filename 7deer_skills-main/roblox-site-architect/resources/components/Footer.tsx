import Link from 'next/link';
import { getGameConfig } from '@/lib/data';

const config = getGameConfig();

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 mt-16 py-8">
      <div className="max-w-6xl mx-auto px-4 text-center text-sm text-gray-500">
        <div className="flex justify-center gap-4 mb-3">
          <Link href="/terms" className="hover:underline">Terms</Link>
          <Link href="/privacy-policy" className="hover:underline">Privacy Policy</Link>
          <Link href="/about" className="hover:underline">About</Link>
        </div>
        <p className="mb-2">
          🏰 {config.game.name} Guide & Tools — Fan-made companion site. Not affiliated with Roblox Corporation.
        </p>
        <p>© {year} All rights reserved.</p>
      </div>
    </footer>
  );
}
