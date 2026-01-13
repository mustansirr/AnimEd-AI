export default function Footer() {
  return (
    <footer className="bg-gray-900">
      <div className="mx-auto max-w-7xl px-6 py-12 md:flex md:items-center md:justify-between lg:px-8">
        <div className="flex justify-center md:order-2">
          <p className="text-center text-xs leading-5 text-gray-400">
             &copy; {new Date().getFullYear()} Agentic AI Educational Video Generator. For academic use only.
          </p>
        </div>
        <div className="mt-8 md:order-1 md:mt-0">
          <p className="text-center text-xs leading-5 text-gray-500">
            Project Disclaimer: This is a demonstration project.
          </p>
        </div>
      </div>
    </footer>
  );
}
