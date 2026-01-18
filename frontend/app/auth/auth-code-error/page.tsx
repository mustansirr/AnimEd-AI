import Link from "next/link";

export default function AuthCodeError() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <h1 className="text-4xl font-bold mb-4">Authentication Error</h1>
      <p className="text-lg mb-4">There was an error signing you in.</p>
      <p className="text-gray-600 mb-8">Please try again or contact support.</p>
      <Link href="/" className="text-blue-500 hover:underline">
        Go back to Home
      </Link>
    </div>
  );
}
