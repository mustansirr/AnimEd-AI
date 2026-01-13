export default function Hero() {
  return (
    <section className="flex flex-col items-center justify-center px-4 py-24 text-center bg-white">
      <div className="max-w-3xl space-y-8">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          Generate animated educational videos from text using AI
        </h1>
        <p className="text-lg leading-8 text-gray-600">
          Transform your lesson plans into engaging visual content in minutes. Designed specifically for educators.
        </p>
        <div className="flex items-center justify-center gap-x-6">
          <button className="rounded-md bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
            Get Started with Google
          </button>
        </div>
      </div>
    </section>
  );
}
