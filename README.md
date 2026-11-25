# **Segmentation-Based Memory Management Simulator**

> **Course:** **CSE234 – Operating Systems** | **Session:** **26271** | **Academic Task:** **Project-Based Assessment (Topic #12)**
>
> **Institution:** **Lovely Professional University (LPU), Punjab, India**

---

## **1. Problem Statement & Overview**

In modern operating systems, processes are logically structured into distinct functional regions—such as **Code**, **Data**, and **Stack**—rather than a single linear block of memory. **Segmentation** supports this user-level view of memory by dividing a process’s logical address space into variable-sized segments, each identified by a **segment number** and an **offset**.

This project implements a **Segmentation-Based Memory Management Simulator** that:

1. **Models** **Code**, **Data**, and **Stack** segments with distinct **base addresses**, **limits (sizes)**, and **access permissions** (`R`, `W`, `X`).
2. **Translates** two-dimensional **logical addresses** `(segment_id, offset)` into one-dimensional **physical addresses** (`base + offset`).
3. **Enforces memory protection** by rejecting **out-of-bounds accesses** (`offset < 0` or `offset + size > limit`) and **unauthorized operations** (e.g., attempting to `WRITE` to a read/execute-only `CODE` segment).
4. **Evaluates** **memory utilization**, **segmentation fault rates**, and **external fragmentation** across dynamic allocation and deallocation workloads.

---

## **2. Course Outcomes (CO) & Bloom's Taxonomy Mapping**

| **Mapping Category** | **Code / Level** | **Description & Application in Project** |
| :--- | :--- | :--- |
| **Course Outcome** | **CO4** | **Memory Management & File Systems:** Modeling segment tables, non-contiguous physical memory allocation (`First Fit`, `Best Fit`, `Worst Fit`), hole coalescing, and external fragmentation. |
| **Course Outcome** | **CO5** | **Protection & Security:** Enforcing segment limit bounds checking and `R`/`W`/`X` permission validation to prevent illegal memory access. |
| **Bloom's Level** | **L3 – Apply** | Implementing segment table lookup and logical-to-physical address translation. |
| **Bloom's Level** | **L4 – Analyze** | Detecting and categorizing `LIMIT_VIOLATION` vs. `PERMISSION_VIOLATION` faults and memory holes. |
| **Bloom's Level** | **L5 – Evaluate** | Measuring and comparing memory utilization, fault rates, and external fragmentation across workloads. |

---

## **3. Team Members & Work Distribution**

This project is collaboratively developed by a **3-member group** using feature branches and pull requests in a shared GitHub repository:

| **Team Member** | **Role & Assigned Module** | **Git Branch** | **Key Responsibilities** |
| :--- | :--- | :--- | :--- |
| **Chandra Mauli Tiwari** | **Repo Lead, Physical Memory & Segment Table Manager** | `feat/memory-mauli` | Repository architecture, shared data models (`models.py`), physical memory allocation/deallocation, hole coalescing, external fragmentation tracking (**CO4**), and report integration. |
| **Nathani Aswik** | **Address Translation & Memory Protection Engine** | `feat/translator-aswik` | Logical-to-physical address translation (`translator.py`), segment limit validation, `R`/`W`/`X` permission enforcement, fault diagnostics (**CO4, CO5**), and translator unit tests. |
| **Vennapusa Vishnu Vardhana Reddy** | **Workload Generator, Metrics & Test Suite** | `feat/metrics-vishnu` | Automated test workloads (`metrics.py`, `tests/`), comparative metric analysis (utilization, fault rates, fragmentation), execution logs, and demo screenshots. |

---

## **4. System Architecture & Address Translation Flow**

### **Logical-to-Physical Translation Pipeline**

```text
  Logical Address Request: (Segment_ID, Offset, Access_Type [R/W/X], Size)
                                      │
                                      ▼
                     ┌─────────────────────────────────┐
                     │ 1. Segment Table Lookup         │
                     │    Does Segment_ID exist &      │
                     │    is Valid bit == True?        │
                     └────────────────┬────────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       │ No                          │ Yes
                       ▼                             ▼
           [INVALID_SEGMENT FAULT]      ┌──────────────────────────┐
                                        │ 2. Bounds / Limit Check  │
                                        │    0 <= Offset AND       │
                                        │    Offset + Size <= Limit│
                                        └────────────┬─────────────┘
                                                     │
                                      ┌──────────────┴──────────────┐
                                      │ No                          │ Yes
                                      ▼                             ▼
                          [LIMIT_VIOLATION FAULT]      ┌─────────────────────────┐
                                                       │ 3. Permission Check     │
                                                       │    Is Access_Type in    │
                                                       │    Segment.Permissions? │
                                                       └────────────┬────────────┘
                                                                    │
                                                     ┌──────────────┴──────────────┐
                                                     │ No                          │ Yes
                                                     ▼                             ▼
                                         [PERMISSION_VIOLATION]      ┌───────────────────────────┐
                                                                     │ 4. Physical Address Calc  │
                                                                     │    Phys_Addr = Base+Offset│
                                                                     └──────────────┬────────────┘
                                                                                    │
                                                                                    ▼
                                                                     [SUCCESS: Physical Access]
```

### **Repository Structure**

```text
OS---Segmentation-based-Memory-Management/
├── README.md                  # Project documentation, setup guide, architecture & test matrix
├── .gitignore                 # Python cache and environment exclusions
├── src/
│   ├── models.py              # Shared data classes: Segment, AccessRequest, TranslationResult, MemoryStats
│   ├── memory_manager.py      # Physical memory simulation, First/Best/Worst Fit, hole merging (Mauli)
│   ├── translator.py          # Address translation, bounds checking & R/W/X protection engine (Aswik)
│   ├── metrics.py             # Workload runner, fault counters & fragmentation metrics (Vishnu)
│   └── main.py                # Interactive CLI & automated demonstration entry point
├── tests/
│   ├── test_memory.py         # Unit tests for segment allocation, freeing & hole coalescing
│   ├── test_translator.py     # Unit tests for valid translations, limit faults & permission faults
│   └── test_workloads.py      # End-to-end scenario tests & metric comparisons
└── docs/
    ├── screenshots/           # Execution logs and CLI output captures for project report
    └── report_draft.md        # Formal CSE234 project report
```

---

## **5. Setup & Execution Instructions**

### **Prerequisites**
* **Python 3.10+** (uses standard library `dataclasses`, `enum`, `typing`, and `unittest`—no external dependencies required).
* **Git** for version control.

### **Clone & Run**

```bash
# 1. Clone the repository (replace <your-username> with the GitHub owner username)
git clone https://github.com/CodeAlchemistJee/OS---Segmentation-based-Memory-Management.git
cd OS---Segmentation-based-Memory-Management

# 2. Run the interactive simulator / demo suite
python src/main.py

# 3. Run all automated unit and workload tests
python -m unittest discover -s tests -v
```

---

## **6. Test Cases & Validation Matrix**

The simulator validates both **legitimate segment accesses** and **security/bounds violations** across **Code**, **Data**, and **Stack** segments:

| **Test ID** | **Segment** | **Base / Limit** | **Permissions** | **Request `(Seg, Offset, Op)`** | **Expected Outcome** | **OS Concept Verified** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `CODE` (`0`) | `0` / `256` | `R, X` | `(0, 120, EXECUTE)` | **`OK`** $\rightarrow$ Physical Addr **`120`** | Valid instruction fetch |
| **TC-02** | `DATA` (`1`) | `256` / `512` | `R, W` | `(1, 64, WRITE)` | **`OK`** $\rightarrow$ Physical Addr **`320`** | Valid global/heap write |
| **TC-03** | `STACK` (`2`) | `768` / `128` | `R, W` | `(2, 127, READ)` | **`OK`** $\rightarrow$ Physical Addr **`895`** | Boundary-valid stack read |
| **TC-04** | `CODE` (`0`) | `0` / `256` | `R, X` | `(0, 256, READ)` | **`LIMIT_VIOLATION`** (Rejected) | Off-by-one bounds protection |
| **TC-05** | `STACK` (`2`) | `768` / `128` | `R, W` | `(2, -4, WRITE)` | **`LIMIT_VIOLATION`** (Rejected) | Negative offset / stack overflow guard |
| **TC-06** | `CODE` (`0`) | `0` / `256` | `R, X` | `(0, 32, WRITE)` | **`PERMISSION_VIOLATION`** (Rejected) | Write-protecting executable code |
| **TC-07** | `DATA` (`1`) | `256` / `512` | `R, W` | `(1, 10, EXECUTE)` | **`PERMISSION_VIOLATION`** (Rejected) | Non-executable data (`NX` / DEP) |
| **TC-08** | `UNMAPPED` (`5`) | — | — | `(5, 0, READ)` | **`INVALID_SEGMENT`** (Rejected) | Unallocated segment table lookup |

---

## **7. Performance & Evaluation Metrics**

To satisfy **Bloom's Level L4 & L5**, the simulator logs and compares:

1. **Memory Utilization (%):**
   $$\text{Utilization} = \left(\frac{\text{Total Allocated Segment Sizes}}{\text{Total Physical Memory}}\right) \times 100$$
2. **External Fragmentation Ratio:**
   $$\text{External Fragmentation} = \frac{\text{Total Free Memory} - \text{Largest Contiguous Free Block}}{\text{Total Free Memory}}$$
3. **Access Translation Breakdown:**
   * **Successful Translations (%)**
   * **Limit Violation Rate (%)**
   * **Permission Violation Rate (%)**
   * **Invalid Segment Rate (%)**
4. **Allocation Policy Comparison:** Compares **First Fit**, **Best Fit**, and **Worst Fit** placement strategies under dynamic segment allocation and deallocation sequences.

---

## **8. Limitations & Future Scope**

* **Simulated Physical Memory:** Operates on an abstracted byte-addressable physical memory model rather than hardware MMU registers (`STBR` / `STLR`) or a Translation Lookaside Buffer (**TLB**).
* **Single-Process Focus:** Currently models the segment table of an active process; future versions can add multi-process context switching and shared read-only `CODE` segments across processes.
* **No Memory Compaction or Paged Segmentation:** External fragmentation is measured and minimized via adjacent hole coalescing, though live segment relocation (compaction) and **segmentation with paging** (x86-style) remain potential extensions.

---

## **9. References**

1. **Silberschatz, A., Galvin, P. B., & Gagne, G.** *Operating System Concepts* (10th Edition) — Chapter on Main Memory (Segmentation & Hardware Support).
2. **Tanenbaum, A. S., & Bos, H.** *Modern Operating Systems* (4th Edition) — Memory Management
