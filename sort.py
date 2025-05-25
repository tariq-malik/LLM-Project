def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):  # Last i elements are already in place
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]  # Swap
    return arr

# Example usage
arr = [64, 25, 12, 22, 11]
sorted_arr = bubble_sort(arr)
print("Sorted array:", sorted_arr)



