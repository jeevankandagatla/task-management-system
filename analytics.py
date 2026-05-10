import pandas as pd
import numpy as np

def calculate_task_analytics(tasks):
    if not tasks:
        return {
            'total_tasks': 0,
            'completed_tasks': 0,
            'pending_tasks': 0,
            'completion_percentage': 0
        }
    
    # Convert tasks to a Pandas DataFrame
    df = pd.DataFrame(tasks)
    
    total_tasks = len(df)
    completed_tasks = len(df[df['status'] == 'Completed'])
    pending_tasks = total_tasks - completed_tasks
    
    # Use NumPy for percentage calculation (though basic math works too)
    completion_percentage = np.round((completed_tasks / total_tasks) * 100, 2) if total_tasks > 0 else 0
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_percentage': float(completion_percentage)
    }
