import React from 'react';

const ProgressBar = ({ currentStep, totalSteps }) => {
  const percentage = (currentStep / totalSteps) * 100;

  const steps = [
    { num: 1, label: 'Basic Info' },
    { num: 2, label: 'Experience' },
    { num: 3, label: 'Skills' },
    { num: 4, label: 'Psychometric' },
    { num: 5, label: 'Empathy' },
    { num: 6, label: 'Preferences' },
  ];

  return (
    <div className="w-full">
      <div className="mb-6">
        <div className="flex justify-between mb-3">
          {steps.map((step) => (
            <div key={step.num} className="flex flex-col items-center flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                  currentStep >= step.num
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-300 text-gray-600'
                }`}
              >
                {step.num}
              </div>
              <span className="text-xs mt-2 text-center text-gray-600">{step.label}</span>
            </div>
          ))}
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>

      <p className="text-center text-sm text-gray-600">
        Step {currentStep} of {totalSteps}
      </p>
    </div>
  );
};

export default ProgressBar;
