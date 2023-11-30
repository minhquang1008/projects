/*Daily - BOM - PhaiSinh*/

/*Actual vs Target - Fee Income (Phí giao dịch - Thực tế và chỉ tiêu)*/

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @WorkDaysOfYear INT;
SET @WorkDaysOfYear = (
	SELECT COUNT(*) 
	FROM [Date] 
	WHERE [Work] = 1 
		AND YEAR([Date]) = YEAR(@Date)
);

WITH

[TargetByBranch] AS (
    SELECT 
        [BranchID] 
        , CAST(CAST([Target] AS FLOAT) / @WorkDaysOfYear AS DECIMAL(30,8)) [FeeIncome]
    FROM [DWH-AppData].[dbo].[BMD.FDSTarget]
    WHERE [Year] = YEAR(@Date)
        AND [Measure] = 'Fee Income'
)

, [Rel] AS (
    SELECT DISTINCT
        [account_code] [AccountCode]
        , [broker_id] [BrokerID]
        , [branch_id] [BranchID]
    FROM [relationship]
    WHERE [date] = @Date
)

, [BranchActual] AS (
    SELECT 
        [Rel].[BranchID] [BranchID]
        , SUM([RRE0018].[PhiGiaoDichPHSThu]) [FeeIncome]
    FROM [RRE0018]
    LEFT JOIN [Rel]
        ON [RRE0018].[SoTaiKhoan] = [Rel].[AccountCode]
    WHERE [RRE0018].[Ngay] = @Date
    GROUP BY [Rel].[BranchID]
)

SELECT 
	[TargetByBranch].[BranchID]
	, ISNULL([BranchActual].[FeeIncome],0) [Actual]
    , [TargetByBranch].[FeeIncome] [Target]
FROM [TargetByBranch]
LEFT JOIN [BranchActual]
    ON [TargetByBranch].[BranchID] = [BranchActual].[BranchID]
ORDER BY 1


END
