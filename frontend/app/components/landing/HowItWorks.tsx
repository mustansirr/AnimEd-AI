export default function HowItWorks() {
  const steps = [
    {
      id: 1,
      title: "Enter Topic",
      description: "Simply type your lesson topic or paste your teaching material.",
    },
    {
      id: 2,
      title: "AI Generation",
      description: "Our AI automatically creates a script and matches it with animations.",
    },
    {
      id: 3,
      title: "Download & Teach",
      description: "Review your video, make quick edits, and download for your class.",
    },
  ];

  return (
    <section className="py-24 bg-gray-50">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-base font-semibold leading-7 text-indigo-600">Workflow</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            How It Works
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {steps.map((step) => (
              <div key={step.id} className="flex flex-col items-start text-left">
                <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                  <span className="text-white font-bold">{step.id}</span>
                </div>
                <dt className="text-xl font-semibold leading-7 text-gray-900">
                  {step.title}
                </dt>
                <dd className="mt-4 leading-7 text-gray-600">
                  {step.description}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
