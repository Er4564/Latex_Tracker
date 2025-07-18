import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};

const FilePreview = ({ file, onClose }) => {
  const [activeTab, setActiveTab] = useState('content');
  
  return (
    <Modal isOpen={true} onClose={onClose} title={file.name}>
      <div className="space-y-4">
        {/* Tabs */}
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('content')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'content' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
          >
            Content
          </button>
          <button
            onClick={() => setActiveTab('info')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'info' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
          >
            Info
          </button>
          <button
            onClick={() => setActiveTab('versions')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'versions' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
          >
            Versions ({file.versions?.length || 0})
          </button>
        </div>

        {/* Content */}
        {activeTab === 'content' && (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <pre className="text-sm whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">
                {file.content}
              </pre>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => {
                  const blob = new Blob([file.content], { type: 'text/plain' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = file.name;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Download
              </button>
            </div>
          </div>
        )}

        {activeTab === 'info' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Word Count</label>
                <p className="mt-1 text-sm text-gray-900">{file.word_count}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">File Size</label>
                <p className="mt-1 text-sm text-gray-900">{file.file_size} bytes</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Compilation Status</label>
                <span className={`mt-1 px-2 py-1 rounded text-xs ${
                  file.compilation_status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : file.compilation_status === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {file.compilation_status}
                </span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Source Type</label>
                <p className="mt-1 text-sm text-gray-900">{file.source_type}</p>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Tags</label>
              <div className="mt-1 flex flex-wrap gap-2">
                {file.tags?.map((tag, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            
            {file.notes && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Notes</label>
                <p className="mt-1 text-sm text-gray-900">{file.notes}</p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Created</label>
              <p className="mt-1 text-sm text-gray-900">
                {new Date(file.created_at).toLocaleDateString()}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Updated</label>
              <p className="mt-1 text-sm text-gray-900">
                {new Date(file.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'versions' && (
          <div className="space-y-4">
            {file.versions?.map((version, index) => (
              <div key={version.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-medium">Version {file.versions.length - index}</h4>
                    <p className="text-sm text-gray-500">
                      {new Date(version.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <p>{version.word_count} words</p>
                    <p>{version.file_size} bytes</p>
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded max-h-32 overflow-y-auto">
                  <pre className="text-xs whitespace-pre-wrap font-mono">
                    {version.content.substring(0, 200)}
                    {version.content.length > 200 && '...'}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
};

const CreateYearModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    year: 1,
    description: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/years`, formData);
      onSuccess();
      onClose();
      setFormData({ year: 1, description: '' });
    } catch (error) {
      console.error('Error creating year:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Year">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Academic Year *</label>
          <select
            value={formData.year}
            onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value={1}>Year 1</option>
            <option value={2}>Year 2</option>
            <option value={3}>Year 3</option>
            <option value={4}>Year 4</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            rows="3"
            placeholder="Optional description for this academic year"
          />
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Year
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </Modal>
  );
};

const CreateSemesterModal = ({ isOpen, onClose, onSuccess, years }) => {
  const [formData, setFormData] = useState({
    year_id: '',
    name: 'A',
    description: '',
    start_date: '',
    end_date: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/semesters`, formData);
      onSuccess();
      onClose();
      setFormData({ year_id: '', name: 'A', description: '', start_date: '', end_date: '' });
    } catch (error) {
      console.error('Error creating semester:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Semester">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Academic Year *</label>
          <select
            value={formData.year_id}
            onChange={(e) => setFormData({ ...formData, year_id: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Select a year</option>
            {years.map(year => (
              <option key={year.id} value={year.id}>Year {year.year}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Semester *</label>
          <select
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="A">Semester A</option>
            <option value="B">Semester B</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            rows="2"
            placeholder="Optional description"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Start Date</label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">End Date</label>
            <input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Semester
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </Modal>
  );
};

const CreateTermModal = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null
      };
      await axios.post(`${API}/terms`, data);
      onSuccess();
      onClose();
      setFormData({ name: '', description: '', start_date: '', end_date: '' });
    } catch (error) {
      console.error('Error creating term:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Term">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Name *</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            rows="3"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Start Date</label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">End Date</label>
            <input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Term
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </Modal>
  );
};

const CreateSubjectModal = ({ isOpen, onClose, onSuccess, semesters }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    semester_id: '',
    color: '#3B82F6'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/subjects`, formData);
      onSuccess();
      onClose();
      setFormData({ name: '', description: '', semester_id: '', color: '#3B82F6' });
    } catch (error) {
      console.error('Error creating subject:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Subject">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Name *</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Semester *</label>
          <select
            value={formData.semester_id}
            onChange={(e) => setFormData({ ...formData, semester_id: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Select a semester</option>
            {semesters.map(semester => (
              <option key={semester.id} value={semester.id}>
                Semester {semester.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            rows="3"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Color</label>
          <input
            type="color"
            value={formData.color}
            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
            className="mt-1 block w-full h-10 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Create Subject
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </Modal>
  );
};

const AddFileModal = ({ isOpen, onClose, onSuccess, years, semesters, subjects }) => {
  const [activeTab, setActiveTab] = useState('manual');
  const [formData, setFormData] = useState({
    name: '',
    year_id: '',
    semester_id: '',
    subject_id: '',
    content: '',
    tags: '',
    notes: '',
    source_type: 'manual'
  });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [multiFileMode, setMultiFileMode] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (multiFileMode && selectedFiles.length > 0) {
        // Multi-file upload
        const multiUploadData = {
          files: selectedFiles.map(file => ({
            name: file.name,
            content: file.content
          })),
          subject_id: formData.subject_id,
          semester_id: formData.semester_id,
          tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          notes: formData.notes
        };
        await axios.post(`${API}/files/multi-upload`, multiUploadData);
      } else {
        // Single file upload
        const data = {
          ...formData,
          tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          source_type: activeTab
        };
        await axios.post(`${API}/files`, data);
      }
      onSuccess();
      onClose();
      resetForm();
    } catch (error) {
      console.error('Error creating file:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      year_id: '',
      semester_id: '',
      subject_id: '',
      content: '',
      tags: '',
      notes: '',
      source_type: 'manual'
    });
    setSelectedFiles([]);
    setMultiFileMode(false);
  };

  const handleMultipleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    const fileContents = await Promise.all(
      files.map(file => {
        return new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = (e) => {
            resolve({
              name: file.name,
              content: e.target.result,
              size: file.size
            });
          };
          reader.readAsText(file);
        });
      })
    );

    setSelectedFiles(fileContents);
    setMultiFileMode(true);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formDataUpload = new FormData();
    formDataUpload.append('file', file);
    formDataUpload.append('subject_id', formData.subject_id);
    formDataUpload.append('semester_id', formData.semester_id);
    formDataUpload.append('tags', formData.tags);
    formDataUpload.append('notes', formData.notes);

    try {
      await axios.post(`${API}/files/upload`, formDataUpload, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      onSuccess();
      onClose();
      resetForm();
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const filteredSemesters = semesters.filter(semester => 
    !formData.year_id || semester.year_id === formData.year_id
  );

  const filteredSubjects = subjects.filter(subject => 
    !formData.semester_id || subject.semester_id === formData.semester_id
  );

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New File">
      <div className="space-y-4">
        {/* Tabs */}
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('manual')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'manual' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
          >
            Manual Upload
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'paste' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
          >
            Copy & Paste
          </button>
          <button
            onClick={() => setActiveTab('git')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'git' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
          >
            Git Integration
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Multi-file mode toggle */}
          {activeTab === 'manual' && (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="multiFileMode"
                checked={multiFileMode}
                onChange={(e) => {
                  setMultiFileMode(e.target.checked);
                  if (!e.target.checked) setSelectedFiles([]);
                }}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <label htmlFor="multiFileMode" className="text-sm font-medium text-gray-700">
                Upload multiple files
              </label>
            </div>
          )}

          {/* Common fields */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Year *</label>
              <select
                value={formData.year_id}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  year_id: e.target.value, 
                  semester_id: '', 
                  subject_id: '' 
                })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select a year</option>
                {years.map(year => (
                  <option key={year.id} value={year.id}>Year {year.year}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Semester *</label>
              <select
                value={formData.semester_id}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  semester_id: e.target.value, 
                  subject_id: '' 
                })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select a semester</option>
                {filteredSemesters.map(semester => (
                  <option key={semester.id} value={semester.id}>Semester {semester.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Subject *</label>
              <select
                value={formData.subject_id}
                onChange={(e) => setFormData({ ...formData, subject_id: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value="">Select a subject</option>
                {filteredSubjects.map(subject => (
                  <option key={subject.id} value={subject.id}>{subject.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Tab-specific content */}
          {activeTab === 'manual' && (
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Upload .tex File{multiFileMode ? 's' : ''}
              </label>
              <input
                type="file"
                accept=".tex"
                multiple={multiFileMode}
                onChange={multiFileMode ? handleMultipleFileUpload : handleFileUpload}
                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {multiFileMode && selectedFiles.length > 0 && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Selected Files ({selectedFiles.length}):
                  </h4>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex justify-between items-center text-xs">
                        <span className="truncate">{file.name}</span>
                        <span className="text-gray-500">{(file.size / 1024).toFixed(1)} KB</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'paste' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">File Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">LaTeX Content *</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  rows="10"
                  placeholder="Paste your LaTeX code here..."
                  required
                />
              </div>
            </>
          )}

          {activeTab === 'git' && (
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="font-medium text-yellow-800 mb-2">Git Integration (Coming Soon)</h4>
              <p className="text-sm text-yellow-700">
                This feature will allow you to sync your Overleaf projects via Git. 
                You'll be able to provide a Git repository URL and automatically import .tex files.
              </p>
            </div>
          )}

          {/* Common fields for manual forms */}
          {activeTab !== 'manual' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700">Tags</label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter tags separated by commas"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  rows="3"
                />
              </div>
            </>
          )}

          {activeTab !== 'git' && (
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Add File
              </button>
              <button
                type="button"
                onClick={onClose}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          )}
        </form>
      </div>
    </Modal>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [years, setYears] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedSemester, setSelectedSemester] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [previewFile, setPreviewFile] = useState(null);

  // Modal states
  const [showCreateYear, setShowCreateYear] = useState(false);
  const [showCreateSemester, setShowCreateSemester] = useState(false);
  const [showCreateSubject, setShowCreateSubject] = useState(false);
  const [showAddFile, setShowAddFile] = useState(false);

  // Load data
  const loadData = async () => {
    try {
      setLoading(true);
      const [yearsRes, semestersRes, subjectsRes, filesRes, statsRes] = await Promise.all([
        axios.get(`${API}/years`),
        axios.get(`${API}/semesters`),
        axios.get(`${API}/subjects`),
        axios.get(`${API}/files`),
        axios.get(`${API}/stats`)
      ]);
      
      setYears(yearsRes.data);
      setSemesters(semestersRes.data);
      setSubjects(subjectsRes.data);
      setFiles(filesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Search files
  const searchFiles = async () => {
    if (!searchQuery.trim()) {
      loadData();
      return;
    }

    try {
      const response = await axios.post(`${API}/search`, {
        query: searchQuery,
        term_id: selectedTerm || null,
        subject_id: selectedSubject || null
      });
      setFiles(response.data);
    } catch (error) {
      console.error('Error searching files:', error);
    }
  };

  // Filter files
  const filteredFiles = files.filter(file => {
    if (selectedTerm && file.term_id !== selectedTerm) return false;
    if (selectedSubject && file.subject_id !== selectedSubject) return false;
    return true;
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        searchFiles();
      }
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, selectedTerm, selectedSubject]);

  // Render functions
  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Total Years</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.total_years || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Total Subjects</h3>
          <p className="text-3xl font-bold text-green-600">{stats.total_subjects || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Total Files</h3>
          <p className="text-3xl font-bold text-purple-600">{stats.total_files || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Compilation Status</h3>
          <div className="mt-2 space-y-1">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Success:</span>
              <span className="text-sm font-medium text-green-600">
                {stats.compilation_stats?.success || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Error:</span>
              <span className="text-sm font-medium text-red-600">
                {stats.compilation_stats?.error || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Unknown:</span>
              <span className="text-sm font-medium text-gray-600">
                {stats.compilation_stats?.unknown || 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Files</h3>
        <div className="space-y-3">
          {stats.recent_files?.slice(0, 5).map(file => (
            <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div>
                <h4 className="font-medium">{file.name}</h4>
                <p className="text-sm text-gray-600">
                  {file.word_count} words • {new Date(file.updated_at).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => setPreviewFile(file)}
                className="text-blue-500 hover:text-blue-700"
              >
                View
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderFiles = () => (
    <div className="space-y-6">
      {/* Search and filters */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <select
              value={selectedTerm}
              onChange={(e) => {
                setSelectedTerm(e.target.value);
                setSelectedSubject('');
              }}
              className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Terms</option>
              {terms.map(term => (
                <option key={term.id} value={term.id}>{term.name}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Subjects</option>
              {subjects
                .filter(subject => !selectedTerm || subject.term_id === selectedTerm)
                .map(subject => (
                  <option key={subject.id} value={subject.id}>{subject.name}</option>
                ))}
            </select>
          </div>
          <div>
            <button
              onClick={() => setShowAddFile(true)}
              className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              Add File
            </button>
          </div>
        </div>
      </div>

      {/* Files grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFiles.map(file => {
          const subject = subjects.find(s => s.id === file.subject_id);
          const term = terms.find(t => t.id === file.term_id);
          
          return (
            <div key={file.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">{file.name}</h3>
                  <p className="text-sm text-gray-600">
                    {term?.name} • {subject?.name}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  file.compilation_status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : file.compilation_status === 'error'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {file.compilation_status}
                </span>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Words:</span>
                  <span>{file.word_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span>{file.file_size} bytes</span>
                </div>
                <div className="flex justify-between">
                  <span>Updated:</span>
                  <span>{new Date(file.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
              
              {file.tags && file.tags.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {file.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                      {tag}
                    </span>
                  ))}
                  {file.tags.length > 3 && (
                    <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                      +{file.tags.length - 3} more
                    </span>
                  )}
                </div>
              )}
              
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => setPreviewFile(file)}
                  className="flex-1 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600"
                >
                  Preview
                </button>
                <button
                  onClick={() => {
                    const blob = new Blob([file.content], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = file.name;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="bg-gray-500 text-white px-3 py-2 rounded text-sm hover:bg-gray-600"
                >
                  Export
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderManagement = () => (
    <div className="space-y-6">
      {/* Terms section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Terms</h3>
          <button
            onClick={() => setShowCreateTerm(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Add Term
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {terms.map(term => (
            <div key={term.id} className="border rounded-lg p-4">
              <h4 className="font-medium">{term.name}</h4>
              {term.description && (
                <p className="text-sm text-gray-600 mt-1">{term.description}</p>
              )}
              <div className="mt-2 text-xs text-gray-500">
                {term.start_date && (
                  <span>
                    {new Date(term.start_date).toLocaleDateString()} - 
                    {term.end_date ? new Date(term.end_date).toLocaleDateString() : 'Present'}
                  </span>
                )}
              </div>
              <div className="mt-2 text-sm text-gray-600">
                {subjects.filter(s => s.term_id === term.id).length} subjects
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Subjects section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Subjects</h3>
          <button
            onClick={() => setShowCreateSubject(true)}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Add Subject
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map(subject => {
            const term = terms.find(t => t.id === subject.term_id);
            const subjectFiles = files.filter(f => f.subject_id === subject.id);
            
            return (
              <div key={subject.id} className="border rounded-lg p-4">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: subject.color }}
                  />
                  <div>
                    <h4 className="font-medium">{subject.name}</h4>
                    <p className="text-sm text-gray-600">{term?.name}</p>
                  </div>
                </div>
                {subject.description && (
                  <p className="text-sm text-gray-600 mt-2">{subject.description}</p>
                )}
                <div className="mt-2 text-sm text-gray-600">
                  {subjectFiles.length} files
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your LaTeX files...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-bold text-blue-600">📄</div>
              <h1 className="text-2xl font-bold text-gray-900">LaTeX File Tracker</h1>
            </div>
            <nav className="flex space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded-md font-medium ${
                  currentView === 'dashboard' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('files')}
                className={`px-4 py-2 rounded-md font-medium ${
                  currentView === 'files' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Files
              </button>
              <button
                onClick={() => setCurrentView('management')}
                className={`px-4 py-2 rounded-md font-medium ${
                  currentView === 'management' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Management
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' && renderDashboard()}
        {currentView === 'files' && renderFiles()}
        {currentView === 'management' && renderManagement()}
      </main>

      {/* Modals */}
      <CreateTermModal
        isOpen={showCreateTerm}
        onClose={() => setShowCreateTerm(false)}
        onSuccess={loadData}
      />
      
      <CreateSubjectModal
        isOpen={showCreateSubject}
        onClose={() => setShowCreateSubject(false)}
        onSuccess={loadData}
        terms={terms}
      />
      
      <AddFileModal
        isOpen={showAddFile}
        onClose={() => setShowAddFile(false)}
        onSuccess={loadData}
        terms={terms}
        subjects={subjects}
      />
      
      {previewFile && (
        <FilePreview
          file={previewFile}
          onClose={() => setPreviewFile(null)}
        />
      )}
    </div>
  );
}

export default App;