import React, { useState } from 'react';
import BasicInfoForm from './BasicInfoForm';
import SkillsPicker from './SkillsPicker';
import EmpathyTest from './EmpathyTest';
import PsychometricTest from './PsychometricTest';
import CareerDiscovery from './CareerDiscovery';
import CareerPreferences from './CareerPreferences';
import CompletionScreen from './CompletionScreen';
import ProgressBar from './ProgressBar';
import { API_ENDPOINTS } from '../../config/api';
const STEPS = [
  { id: 1, title: 'Basic Info', component: BasicInfoForm },
  { id: 2, title: 'Skills', component: SkillsPicker },
  { id: 3, title: 'Empathy Map', component: EmpathyTest },
  { id: 4, title: 'Work Style', component: PsychometricTest },
  { id: 5, title: 'Discovery', component: CareerDiscovery },
  { id: 6, title: 'Preferences', component: CareerPreferences },
];
export default function OnboardingFlow() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    basicInfo: {}, skills: [], empathy: {}, psychometric: {}, discovery: {}, preferences: {},
  });
  const [loading, setLoading] = useState(false);
  const CurrentStepComponent = STEPS[currentStep - 1]?.component;
  const handleStepData = (stepName, data) => {
    setFormData(prev => ({ ...prev, [stepName]: data }));
  };
  const handleNext = async () => {
    if (currentStep < STEPS.length) {
      setCurrentStep(currentStep + 1);
    } else {
      await saveOnboarding();
    }
  };
  const handlePrevious = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };
  const saveOnboarding = async () => {
    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.ONBOARDING_SAVE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (response.ok) {
        setCurrentStep(STEPS.length + 1);
      }
    } catch (error) {
      console.error('Onboarding save failed:', error);
    } finally {
      setLoading(false);
    }
  };
  if (currentStep === STEPS.length + 1) {
    return <CompletionScreen />;
  }
  return (
    <div className="onboarding-container">
      <ProgressBar current={currentStep} total={STEPS.length} />
      <div className="step-content">
        {CurrentStepComponent && (
          <CurrentStepComponent 
            data={formData}
            onSave={(data) => handleStepData(STEPS[currentStep - 1].title.toLowerCase().replace(' ', ''), data)}
          />
        )}
      </div>
      <div className="step-navigation">
        <button onClick={handlePrevious} disabled={currentStep === 1}>Previous</button>
        <button onClick={handleNext} disabled={loading}>{currentStep === STEPS.length ? 'Complete' : 'Next'}</button>
      </div>
    </div>
  );
}
