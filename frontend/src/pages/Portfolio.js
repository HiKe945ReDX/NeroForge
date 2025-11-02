import React, { useState, useEffect } from 'react';
import { FolderIcon, DownloadIcon, EyeIcon, EditIcon } from 'lucide-react';
import { portfolioService } from '../services/api';
import toast from 'react-hot-toast';

const Portfolio = () => {
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  const [loading, setLoading] = useState(false);
  const [portfolio, setPortfolio] = useState(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await portfolioService.getTemplates();
      setTemplates(response.data.templates || []);
    } catch (error) {
      toast.error('Failed to load templates');
    }
  };

  const generatePortfolio = async () => {
    setLoading(true);
    try {
      const response = await portfolioService.generatePortfolio({
        user_id: 'demo_user',
        template: selectedTemplate,
        sections: ['summary', 'skills', 'projects', 'experience'],
        data: {
          name: 'Demo User',
          title: 'AI Engineer',
          skills: ['Python', 'TensorFlow', 'React', 'FastAPI'],
          projects: [
            { name: 'Guidora AI Platform', description: 'Complete career guidance platform' },
            { name: 'Machine Learning Pipeline', description: 'Automated ML workflow system' }
          ]
        }
      });
      setPortfolio(response.data);
      toast.success('Portfolio generated successfully!');
    } catch (error) {
      toast.error('Portfolio generation failed');
    } finally {
      setLoading(false);
    }
  };

  const exportPortfolio = async (format) => {
    try {
      const response = await portfolioService.exportPortfolio({
        user_id: 'demo_user',
        format: format
      });
      toast.success(`Portfolio exported as ${format.toUpperCase()}!`);
      window.open(response.data.download_url, '_blank');
    } catch (error) {
      toast.error('Export failed');
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Portfolio Builder</h1>
        <p className="text-lg text-gray-600">Create professional portfolios with AI assistance</p>
      </div>

      {/* Templates Selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Choose Template</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {templates.map((template) => (
            <div
              key={template.id}
              onClick={() => setSelectedTemplate(template.id)}
              className={`cursor-pointer p-4 rounded-lg border-2 transition-colors ${
                selectedTemplate === template.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h3 className="font-semibold text-gray-900">{template.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{template.description}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {template.features?.map((feature, index) => (
                  <span key={index} className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                    {feature}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Generate Portfolio */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <button
            onClick={generatePortfolio}
            disabled={loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Generating Portfolio...' : 'Generate Portfolio'}
          </button>
        </div>

        {portfolio && (
          <div className="mt-8 p-6 bg-gray-50 rounded-xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Generated!</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Template</h4>
                <p className="text-gray-600 capitalize">{portfolio.template}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Sections</h4>
                <div className="flex flex-wrap gap-2">
                  {portfolio.sections?.map((section, index) => (
                    <span key={index} className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                      {section}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={() => exportPortfolio('pdf')}
                className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
              >
                <DownloadIcon className="w-4 h-4" />
                <span>Export PDF</span>
              </button>
              <button
                onClick={() => exportPortfolio('html')}
                className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
              >
                <DownloadIcon className="w-4 h-4" />
                <span>Export HTML</span>
              </button>
              <button
                onClick={() => window.open(portfolio.shareable_link, '_blank')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
              >
                <EyeIcon className="w-4 h-4" />
                <span>Preview</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Portfolio;
